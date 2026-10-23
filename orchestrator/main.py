#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import dataclasses
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

import docker_stats
import k6_runner
from config import BenchmarkConfig, ProtocolConfig, load_config
from ssh_client import RemoteHost

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("orchestrator")

@dataclasses.dataclass
class TestCaseResult:
    protocol: str
    size: int
    repetition: int
    
    latency_avg_ms: Optional[float]
    latency_med_ms: Optional[float]
    latency_p95_ms: Optional[float]
    latency_p99_ms: Optional[float]
    latency_max_ms: Optional[float]
    throughput_rps: Optional[float]
    checks_passed: Optional[int]
    checks_failed: Optional[int]
    k6_success: bool
    
    cpu_avg_pct: Optional[float]
    cpu_max_pct: Optional[float]
    mem_avg_mib: Optional[float]
    mem_max_mib: Optional[float]
    stats_sample_count: int

def _duration_and_throughput_metric_names(protocol_name: str) -> tuple[str, str]:
    if protocol_name == "rest":
        return "http_req_duration", "http_reqs"
    if protocol_name == "grpc":
        return "grpc_req_duration", "iterations"
    raise ValueError(f"Protocolo desconhecido: {protocol_name}")

def run_single_case(
    host: RemoteHost,
    protocol: ProtocolConfig,
    size: int,
    repetition: int,
    cfg: BenchmarkConfig,
) -> TestCaseResult:
    tag = f"{protocol.name}_{size}_rep{repetition}"
    logger.info("=== Iniciando caso: %s ===", tag)

    container_id = docker_stats.resolve_container_id(host, protocol.compose_service)

    collector_pid = docker_stats.start_collector(
        host, container_id, tag, cfg.run.stats_interval_seconds
    )

    duration_metric, throughput_metric = _duration_and_throughput_metric_names(protocol.name)

    env = {
        "SIZE": str(size),
        "VUS": str(cfg.run.vus),
        "DURATION": cfg.run.duration,
        protocol.target_env_var: protocol.target_value,
    }

    try:

        k6_result = k6_runner.run_k6(
            script_path=protocol.k6_script,
            k6_binary=cfg.run.k6_binary,
            env=env,
            duration_metric=duration_metric,
            throughput_metric=throughput_metric,
            summary_dir=str(Path(cfg.run.output_dir) / "raw"),
            tag=tag,
        )
    finally:

        docker_stats.stop_collector(host, collector_pid)

    samples = docker_stats.fetch_and_parse(host, tag, str(Path(cfg.run.output_dir) / "raw"))
    stats_summary = docker_stats.StatsSummary.from_samples(samples)

    if stats_summary.sample_count == 0:
        logger.warning(
            "Nenhuma amostra de docker stats coletada para %s — verifique se "
            "o container '%s' (serviço '%s') estava realmente rodando.",
            tag, container_id, protocol.compose_service,
        )

    if not k6_result.success:
        logger.warning("k6 reportou falha para %s (ver logs/summary em %s)", tag, k6_result.raw_summary_path)

    return TestCaseResult(
        protocol=protocol.name,
        size=size,
        repetition=repetition,
        latency_avg_ms=k6_result.avg_ms,
        latency_med_ms=k6_result.med_ms,
        latency_p95_ms=k6_result.p95_ms,
        latency_p99_ms=k6_result.p99_ms,
        latency_max_ms=k6_result.max_ms,
        throughput_rps=k6_result.throughput_rate,
        checks_passed=k6_result.checks_passed,
        checks_failed=k6_result.checks_failed,
        k6_success=k6_result.success,
        cpu_avg_pct=stats_summary.cpu_avg,
        cpu_max_pct=stats_summary.cpu_max,
        mem_avg_mib=stats_summary.mem_used_avg_mib,
        mem_max_mib=stats_summary.mem_used_max_mib,
        stats_sample_count=stats_summary.sample_count,
    )

def write_results_csv(results: List[TestCaseResult], path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [f.name for f in dataclasses.fields(TestCaseResult)]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(dataclasses.asdict(r))
    logger.info("Resultados consolidados salvos em %s (%d linhas)", path, len(results))

def main() -> int:
    parser = argparse.ArgumentParser(description="Orquestrador de benchmark REST vs gRPC")
    parser.add_argument("--config", required=True, help="Caminho do config.yaml")
    parser.add_argument(
        "--only", choices=["rest", "grpc"], default=None,
        help="Roda apenas um protocolo (por padrão, roda todos os configurados)",
    )
    parser.add_argument(
        "--sizes", default=None,
        help="Lista de volumes separada por vírgula (ex.: 1000,10000). "
             "Por padrão usa run.sizes do config.yaml.",
    )
    parser.add_argument(
        "--repetitions", type=int, default=None,
        help="Sobrescreve run.repetitions do config.yaml",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)

    protocols = [p for p in cfg.protocols if args.only is None or p.name == args.only]
    if not protocols:
        logger.error("Nenhum protocolo selecionado (--only=%s não encontrado no config)", args.only)
        return 1

    sizes = (
        [int(s) for s in args.sizes.split(",")]
        if args.sizes
        else cfg.run.sizes
    )
    repetitions = args.repetitions or cfg.run.repetitions

    logger.info(
        "Plano de execução: protocolos=%s | volumes=%s | repetições=%d",
        [p.name for p in protocols], sizes, repetitions,
    )

    results: List[TestCaseResult] = []

    with RemoteHost(
        host=cfg.ssh.host,
        port=cfg.ssh.port,
        user=cfg.ssh.user,
        key_path=cfg.ssh.resolved_key_path(),
    ) as host:
        total_cases = len(protocols) * len(sizes) * repetitions
        case_num = 0

        for protocol in protocols:
            for size in sizes:
                for rep in range(1, repetitions + 1):
                    case_num += 1
                    logger.info("--- Caso %d/%d ---", case_num, total_cases)

                    try:
                        result = run_single_case(host, protocol, size, rep, cfg)
                        results.append(result)

                        write_results_csv(results, str(Path(cfg.run.output_dir) / "results.csv"))
                    except Exception:
                        logger.exception(
                            "Falha inesperada no caso protocolo=%s size=%d rep=%d — "
                            "pulando para o próximo caso.",
                            protocol.name, size, rep,
                        )

                    if case_num < total_cases:
                        time.sleep(cfg.run.cooldown_seconds)

    output_csv = str(Path(cfg.run.output_dir) / "results.csv")
    write_results_csv(results, output_csv)

    failed = [
        r for r in results
        if not r.k6_success
        or r.stats_sample_count == 0
        or ((r.checks_passed or 0) + (r.checks_failed or 0)) == 0
    ]
    if failed:
        logger.warning(
            "%d de %d casos tiveram problemas (k6 falhou, sem amostras de docker stats, ou nenhum check executado). "
            "Revise results.csv antes de usar os dados na análise.",
            len(failed), len(results),
        )

    return 0

if __name__ == "__main__":
    sys.exit(main())

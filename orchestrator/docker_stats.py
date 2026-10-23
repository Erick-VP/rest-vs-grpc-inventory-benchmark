# A janela segue a ordem causal: iniciar coletor, executar k6 e parar coletor; não compara relógios.
from __future__ import annotations

import csv
import logging
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ssh_client import RemoteHost

logger = logging.getLogger(__name__)

REMOTE_STATS_DIR = "/tmp/benchmark_stats"

@dataclass
class StatSample:
    timestamp: float  

    cpu_percent: float
    mem_used_mib: float
    mem_limit_mib: float
    mem_percent: float

@dataclass
class StatsSummary:
    sample_count: int
    cpu_avg: Optional[float]
    cpu_max: Optional[float]
    mem_used_avg_mib: Optional[float]
    mem_used_max_mib: Optional[float]
    mem_percent_avg: Optional[float]
    mem_percent_max: Optional[float]

    @classmethod
    def from_samples(cls, samples: List[StatSample]) -> "StatsSummary":
        if not samples:

            return cls(0, None, None, None, None, None, None)
        cpu_vals = [s.cpu_percent for s in samples]
        mem_used_vals = [s.mem_used_mib for s in samples]
        mem_pct_vals = [s.mem_percent for s in samples]
        return cls(
            sample_count=len(samples),
            cpu_avg=statistics.mean(cpu_vals),
            cpu_max=max(cpu_vals),
            mem_used_avg_mib=statistics.mean(mem_used_vals),
            mem_used_max_mib=max(mem_used_vals),
            mem_percent_avg=statistics.mean(mem_pct_vals),
            mem_percent_max=max(mem_pct_vals),
        )

def resolve_container_id(host: RemoteHost, compose_service: str) -> str:

    result = host.run(
        f'docker ps --filter "label=com.docker.compose.service={compose_service}" '
        f'--format "{{{{.ID}}}}"'
    )
    container_id = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    if not container_id:
        raise RuntimeError(
            f"Nenhum container encontrado para o serviço '{compose_service}'. "
            f"Confirme que 'docker compose up' está rodando no servidor."
        )
    return container_id

def _remote_csv_path(tag: str) -> str:
    return f"{REMOTE_STATS_DIR}/{tag}.csv"

def start_collector(
    host: RemoteHost, container_id: str, tag: str, interval_seconds: float
) -> int:

    remote_csv = _remote_csv_path(tag)
    loop = (
        f"mkdir -p {REMOTE_STATS_DIR} && "
        f"rm -f {remote_csv} && "
        f"while true; do "
        f'  ts=$(date +%s.%3N); '
        f'  line=$(docker stats --no-stream --format "{{{{.CPUPerc}}}}|{{{{.MemUsage}}}}|{{{{.MemPerc}}}}" {container_id}); '
        f'  echo "$ts|$line" >> {remote_csv}; '
        f"  sleep {interval_seconds}; "
        f"done"
    )
    return host.start_background(loop)

def stop_collector(host: RemoteHost, pid: int) -> None:
    host.stop_background(pid)

def fetch_and_parse(host: RemoteHost, tag: str, local_dir: str) -> List[StatSample]:

    remote_csv = _remote_csv_path(tag)
    local_path = Path(local_dir) / f"{tag}_docker_stats.csv"
    local_path.parent.mkdir(parents=True, exist_ok=True)

    host.download_file(remote_csv, str(local_path))
    host.remove_remote_file(remote_csv)

    samples: List[StatSample] = []
    with open(local_path, "r", encoding="utf-8") as f:
        for lineno, raw_line in enumerate(f, start=1):
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                ts_str, cpu_str, mem_usage_str, mem_pct_str = raw_line.split("|")
                cpu = float(cpu_str.strip().rstrip("%"))
                used_str, limit_str = mem_usage_str.split("/")
                mem_used = _parse_mib(used_str.strip())
                mem_limit = _parse_mib(limit_str.strip())
                mem_pct = float(mem_pct_str.strip().rstrip("%"))
                samples.append(
                    StatSample(
                        timestamp=float(ts_str),
                        cpu_percent=cpu,
                        mem_used_mib=mem_used,
                        mem_limit_mib=mem_limit,
                        mem_percent=mem_pct,
                    )
                )
            except (ValueError, IndexError) as exc:

                logger.warning(
                    "Linha %d de %s ignorada (formato inesperado: %r): %s",
                    lineno, local_path, raw_line, exc,
                )
    return samples

def _parse_mib(value: str) -> float:

    value = value.strip()
    if value.endswith("GiB"):
        return float(value[:-3]) * 1024
    if value.endswith("MiB"):
        return float(value[:-3])
    if value.endswith("KiB"):
        return float(value[:-3]) / 1024
    if value.endswith("B"):
        return float(value[:-1]) / (1024 * 1024)

    raise ValueError(f"Não sei converter '{value}' para MiB")

from __future__ import annotations

import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

@dataclass
class K6Result:
    success: bool
    duration_metric: str  
    avg_ms: Optional[float]
    min_ms: Optional[float]
    med_ms: Optional[float]
    max_ms: Optional[float]
    p90_ms: Optional[float]
    p95_ms: Optional[float]
    p99_ms: Optional[float]
    throughput_count: Optional[int]
    throughput_rate: Optional[float]  
    checks_passed: Optional[int]
    checks_failed: Optional[int]
    raw_summary_path: str

def _extract_metric(metrics: Dict, name: str) -> Dict:
    return metrics.get(name) or {}

def run_k6(
    script_path: str,
    k6_binary: str,
    env: Dict[str, str],
    duration_metric: str,
    throughput_metric: str,
    summary_dir: str,
    tag: str,
    timeout_seconds: float = 600.0,
) -> K6Result:

    summary_path = Path(summary_dir) / f"{tag}_k6_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        k6_binary,
        "run",
        f"--summary-export={summary_path}",
        
        "--summary-trend-stats=avg,min,med,max,p(90),p(95),p(99)",
        "--quiet",
        script_path,
    ]

    full_env = {**_os_environ(), **env}

    logger.info("Executando k6: %s (env=%s)", " ".join(cmd), env)
    proc = subprocess.run(
        cmd,
        env=full_env,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )

    if proc.returncode != 0:
        logger.warning(
            "k6 terminou com código %s para tag=%s. stderr (últimas linhas): %s",
            proc.returncode,
            tag,
            "\n".join(proc.stderr.strip().splitlines()[-10:]),
        )

    if not summary_path.exists():
        return K6Result(
            success=False,
            duration_metric=duration_metric,
            avg_ms=None, min_ms=None, med_ms=None, max_ms=None,
            p90_ms=None, p95_ms=None, p99_ms=None,
            throughput_count=None, throughput_rate=None,
            checks_passed=None, checks_failed=None,
            raw_summary_path=str(summary_path),
        )

    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metrics = data.get("metrics", {})
    _checks = metrics.get("checks") or {}
    if (_checks.get("passes", 0) + _checks.get("fails", 0)) == 0:

        logger.warning(
            "k6 terminou mas NENHUM check foi executado para tag=%s. "
            "stderr (últimas linhas): %s",
            tag, "\n".join(proc.stderr.strip().splitlines()[-5:]),
        )
    duration = _extract_metric(metrics, duration_metric)
    throughput = _extract_metric(metrics, throughput_metric)
    checks = _extract_metric(metrics, "checks")

    return K6Result(
        success=(proc.returncode == 0),
        duration_metric=duration_metric,
        avg_ms=duration.get("avg"),
        min_ms=duration.get("min"),
        med_ms=duration.get("med"),
        max_ms=duration.get("max"),
        p90_ms=duration.get("p(90)"),
        p95_ms=duration.get("p(95)"),
        p99_ms=duration.get("p(99)"),
        throughput_count=throughput.get("count"),
        throughput_rate=throughput.get("rate"),
        checks_passed=checks.get("passes"),
        checks_failed=checks.get("fails"),
        raw_summary_path=str(summary_path),
    )

def _os_environ() -> Dict[str, str]:
    import os
    return dict(os.environ)

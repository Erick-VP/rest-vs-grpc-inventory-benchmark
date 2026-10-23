from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import List

import yaml

@dataclasses.dataclass
class SSHConfig:

    host: str
    port: int = 22
    user: str = "root"
    key_path: str = "~/.ssh/id_ed25519"

    def resolved_key_path(self) -> str:
        return str(Path(self.key_path).expanduser())

@dataclasses.dataclass
class ProtocolConfig:

    name: str  
    k6_script: str  
    target_env_var: str  
    target_value: str  
    compose_service: str  

@dataclasses.dataclass
class RunConfig:

    sizes: List[int] = dataclasses.field(
        default_factory=lambda: [1000, 10000, 50000, 100000]
    )
    repetitions: int = 5
    vus: int = 10
    duration: str = "30s"
    stats_interval_seconds: float = 1.0
    cooldown_seconds: float = 10.0
    k6_binary: str = "k6"
    output_dir: str = "results"

@dataclasses.dataclass
class BenchmarkConfig:
    ssh: SSHConfig
    protocols: List[ProtocolConfig]
    run: RunConfig

def load_config(path: str) -> BenchmarkConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    ssh = SSHConfig(**raw["ssh"])
    protocols = [ProtocolConfig(**p) for p in raw["protocols"]]
    run = RunConfig(**raw.get("run", {}))

    return BenchmarkConfig(ssh=ssh, protocols=protocols, run=run)

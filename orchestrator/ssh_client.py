from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import paramiko

logger = logging.getLogger(__name__)

@dataclass
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str

class RemoteHost:

    def __init__(self, host: str, port: int, user: str, key_path: str, timeout: float = 10.0):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            hostname=host,
            port=port,
            username=user,
            key_filename=key_path,
            timeout=timeout,
        )
        logger.info("Conectado via SSH em %s@%s:%s", user, host, port)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "RemoteHost":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def run(self, command: str, timeout: float = 30.0) -> CommandResult:

        stdin, stdout, stderr = self._client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()
        return CommandResult(exit_code=exit_code, stdout=out, stderr=err)

    def start_background(self, command: str) -> int:

        # setsid cria um grupo próprio; encerrar o grupo pelo PID também encerra os filhos do coletor.
        wrapped = f"setsid nohup bash -c '{command}' > /dev/null 2>&1 & echo $!"
        result = self.run(wrapped, timeout=10.0)
        if result.exit_code != 0 or not result.stdout.strip().isdigit():
            raise RuntimeError(
                f"Falha ao iniciar processo em background: "
                f"exit={result.exit_code} stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        pid = int(result.stdout.strip())
        logger.debug("Processo em background iniciado, PID=%s", pid)
        return pid

    def stop_background(self, pid: int, grace_period: float = 1.0) -> None:

        self.run(f"kill -TERM -{pid} 2>/dev/null; true", timeout=10.0)
        time.sleep(grace_period)
        self.run(f"kill -KILL -{pid} 2>/dev/null; true", timeout=10.0)
        logger.debug("Processo em background PID=%s encerrado", pid)

    def download_file(self, remote_path: str, local_path: str) -> None:
        sftp = self._client.open_sftp()
        try:
            sftp.get(remote_path, local_path)
        finally:
            sftp.close()

    def remove_remote_file(self, remote_path: str) -> None:
        self.run(f"rm -f {remote_path}")

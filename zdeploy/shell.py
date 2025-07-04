"""Simple shell helpers."""

import subprocess
from typing import Tuple


def execute(cmd: str) -> Tuple[str, int]:
    """Execute ``cmd`` in a shell and return output and return code."""

    with subprocess.Popen(
        f"{cmd} 2>&1",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    ) as proc:
        std_out, _ = proc.communicate()
        rc = proc.returncode
    return std_out, rc

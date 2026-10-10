"""Build the consumer payload through its public build script."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
BUILD = ROOT / ".engineering/scripts/build_template.py"


def build(destination: Path) -> Path:
    """Build a fresh consumer directory, failing with the script's output."""
    result = subprocess.run(
        [sys.executable, str(BUILD), str(destination)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return destination

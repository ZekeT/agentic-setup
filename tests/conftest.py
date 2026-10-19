"""Expose the source checkout to tests without packaging it into applications."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

pytest_plugins = ["skill_support"]

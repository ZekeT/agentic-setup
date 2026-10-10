"""Keep embedded project suites isolated and share only immutable preparation."""

import shutil
from pathlib import Path

import pytest

from .immutable import unchanged
from .template_build import build

# test_semantic_fixtures runs these suites from each fixture's own project root.
collect_ignore = ["fixtures"]


@pytest.fixture(scope="session")
def built_template(tmp_path_factory):
    """Build the consumer payload once; a test that writes to it fails teardown."""
    root = build(tmp_path_factory.mktemp("template") / "project")
    with unchanged(root):
        yield root


@pytest.fixture
def generated(built_template):
    """Copy the shared build to a fresh writable destination for one test."""

    def copy(destination: Path) -> Path:
        shutil.copytree(built_template, destination, symlinks=True)
        return destination

    return copy

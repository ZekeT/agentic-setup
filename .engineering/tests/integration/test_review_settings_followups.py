"""Review settings reject typos and keep executable configuration out of prose."""

import pytest

from .test_review_tiers import CONFIG, commit_base_settings, settings_text
from .test_verification import change_plan, prepare
from .test_verification import repo as repo

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("where", ["base", "proposed"])
def test_unknown_review_keys_rejected_in_both_versions(repo, where):
    good = settings_text(["**"])
    bad = good + "typo = []\n"
    commit_base_settings(repo, bad if where == "base" else good)
    (repo / CONFIG).write_text(good if where == "base" else bad)
    change_plan(repo, paths=["app.txt", CONFIG])
    assert "unknown" in prepare(repo, status=1)["error"]

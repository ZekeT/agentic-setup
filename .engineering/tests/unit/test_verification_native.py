"""Native review identities and coverage, decided from committed fingerprints."""

import pytest
from engineering.verification_semantic import native_ids, reject_uncovered

FILE = {"sha256": "f" * 64, "executable": False}
UNCOVERED = (
    "Native review does not cover proposed content; make a scoped checkpoint "
    "including additions, deletions and modes, then obtain both native axes"
)


def rejection(decide, *args):
    with pytest.raises(ValueError) as error:
        decide(*args)
    return str(error.value)


@pytest.mark.parametrize("length", [40, 64])
def test_full_commit_ids_are_accepted(report, length):
    native = report("spec", reviewed_commit="a" * length, comparison_base="b" * 40)
    assert native_ids(native) == ("a" * length, "b" * 40)


@pytest.mark.parametrize(
    "changes",
    [
        {"reviewed_commit": "abc123"},
        {"reviewed_commit": "A" * 40},
        {"comparison_base": "main"},
        {"comparison_base": None},
        {"reviewed_commit": "a" * 41},
    ],
)
def test_abbreviated_or_symbolic_identities_are_rejected(report, changes):
    assert rejection(native_ids, report("standards", **changes)) == (
        "Native review requires full reviewed_commit and comparison_base IDs"
    )


def inputs(files, paths=("app.txt",)):
    return {"files": files, "plan": {"paths": list(paths)}}


def test_a_checkpoint_matching_every_proposed_file_covers_it():
    reject_uncovered({"app.txt": FILE}, {"app.txt"}, inputs({"app.txt": FILE}))


@pytest.mark.parametrize(
    "committed,baseline,proposed,paths",
    [
        # Addition: the proposed new file is absent from the checkpoint.
        (
            {"app.txt": FILE},
            {"app.txt"},
            {"app.txt": FILE, "new.txt": FILE},
            ("app.txt", "new.txt"),
        ),
        # Deletion: the checkpoint still holds a proposed removal.
        ({"app.txt": FILE}, {"app.txt"}, {"app.txt": None}, ("app.txt",)),
        # Mode: the proposed executable bit is not committed.
        (
            {"app.txt": FILE},
            {"app.txt"},
            {"app.txt": {**FILE, "executable": True}},
            ("app.txt",),
        ),
        # Content: different bytes at the checkpoint.
        (
            {"app.txt": {**FILE, "sha256": "a" * 64}},
            {"app.txt"},
            {"app.txt": FILE},
            ("app.txt",),
        ),
        # Extra: the checkpoint commits a file outside the proposal.
        (
            {"app.txt": FILE, "extra.txt": FILE},
            {"app.txt"},
            {"app.txt": FILE},
            ("app.txt",),
        ),
    ],
)
def test_checkpoints_missing_any_change_are_rejected(
    committed, baseline, proposed, paths
):
    assert (
        rejection(reject_uncovered, committed, baseline, inputs(proposed, paths))
        == UNCOVERED
    )

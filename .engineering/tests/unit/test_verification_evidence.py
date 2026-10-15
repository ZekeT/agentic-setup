"""Evidence decisions from written-down records: reports, history, staleness, outcome."""

import pytest
from engineering.verification_evidence import (
    SESSIONS,
    admit,
    outcome,
    reject_unsupported_schema,
    stale,
    validate_records,
    validate_report,
)
from engineering.verification_facts import EvidenceFacts, StoredRecord, frozen_json

from .conftest import TOKEN, passed

OLD = "0" * 64
HISTORY = ".engineering/state/verification/example-1/previous.json"
FIELDS = (
    "Report fields: snapshot, role, reviewer, independent, verdict, summary, "
    "findings, coverage_gaps"
)


def rejection(decide, *args):
    with pytest.raises(ValueError) as error:
        decide(*args)
    return str(error.value)


def stored(data, *history):
    """The stored record followed by the history its carried reports name."""
    first = StoredRecord(".engineering/state/verification/example.json", data)
    return (first, *history)


def previous(data, path=HISTORY):
    return StoredRecord(path, frozen_json(data))


def carried(report, source=OLD):
    """A report carried from the source snapshot to the current one."""
    return {**report, "snapshot": TOKEN, "carried_from": source}


# Report validation


@pytest.mark.parametrize("role", ["standards", "spec", "behavioral", "security"])
def test_complete_reports_are_accepted_for_every_role(report, role):
    validate_report(report(role), TOKEN)


def test_empty_findings_and_gaps_and_full_length_ids_are_accepted(report):
    validate_report(report("spec", reviewed_commit="d" * 64), TOKEN)


@pytest.mark.parametrize("missing", ["reviewed_commit", "comparison_base"])
def test_native_reports_require_both_review_identities(report, missing):
    native = report("standards")
    del native[missing]
    assert rejection(validate_report, native, TOKEN) == (
        "Native reports require reviewed_commit and comparison_base"
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"extra": True},
        {"carried_from": OLD},
        {"reviewed_commit": "c" * 40},
    ],
)
def test_unexpected_fields_are_rejected(report, changes):
    assert rejection(validate_report, report(**changes), TOKEN) == FIELDS


def test_missing_fields_are_rejected(report):
    incomplete = report()
    del incomplete["coverage_gaps"]
    assert rejection(validate_report, incomplete, TOKEN) == FIELDS


@pytest.mark.parametrize(
    "changes,message",
    [
        (
            {"snapshot": OLD},
            "STALE report: snapshot differs; reverify current content",
        ),
        (
            {"independent": "true"},
            "Independent review required; implementer self-review is not proof",
        ),
        (
            {"independent": False},
            "Independent review required; implementer self-review is not proof",
        ),
        ({"verdict": "OK"}, "Report verdict must be PASS, FAIL or CONCERNS"),
        ({"summary": " "}, "Report summary must be nonempty text"),
        ({"reviewer": 1}, "Report reviewer must be nonempty text"),
        ({"findings": "none"}, "findings: expected a list"),
        ({"coverage_gaps": [""]}, "coverage_gaps: expected nonempty strings"),
    ],
)
def test_invalid_reports_are_rejected(report, changes, message):
    assert rejection(validate_report, report(**changes), TOKEN) == message


def test_unknown_roles_are_rejected(report):
    assert (
        rejection(validate_report, report("maintainability"), TOKEN)
        == "Unknown reviewer role"
    )


@pytest.mark.parametrize("verdict", ["FAIL", "CONCERNS"])
def test_failing_verdicts_are_valid_reports(report, verdict):
    validate_report(report(verdict=verdict, findings=["Broken"]), TOKEN)


# Stored records


def test_a_complete_record_is_accepted(record, report):
    validate_records(stored(record(report("standards"), report("behavioral"))))


@pytest.mark.parametrize(
    "changes",
    [
        {"schema_version": 2},
        {"schema_version": "3"},
        {"schema_version": True},
        {"inputs": []},
        {"requirements": None},
        {"reports": []},
        {"checks": {}},
        {"snapshot": None},
    ],
)
def test_unsupported_record_structure_is_rejected(record, changes):
    assert rejection(validate_records, stored({**record(), **changes})) == (
        "Invalid or unsupported verification record; prepare again"
    )


def test_a_record_without_a_plan_is_rejected(record):
    data = record()
    data["inputs"]["plan"] = ["app.txt"]
    assert rejection(validate_records, stored(data)) == "Invalid stored plan"


def test_a_malformed_stored_plan_is_rejected_by_its_shape(record):
    data = record()
    data["inputs"]["plan"]["checks"] = []
    assert rejection(validate_records, stored(data)) == (
        "checks: nonempty argv list required"
    )


@pytest.mark.parametrize(
    "change",
    [
        lambda requirements: requirements.update(extra=1),
        lambda requirements: requirements.update(floor="trivial"),
        lambda requirements: requirements.update(roles=["behavioral"]),
        lambda requirements: requirements.pop("checks"),
    ],
)
def test_invalid_stored_requirements_are_rejected(record, change):
    data = record()
    change(data["requirements"])
    assert rejection(validate_records, stored(data)) == (
        "Invalid stored requirements; prepare again"
    )


def test_a_stored_report_must_be_an_object(record):
    data = record()
    data["reports"]["behavioral"] = "PASS"
    assert rejection(validate_records, stored(data)) == "Invalid stored report"


def test_a_stored_report_is_validated_like_a_new_one(record):
    data = record()
    data["reports"]["behavioral"] = {"verdict": "PASS"}
    assert rejection(validate_records, stored(data)) == FIELDS


def test_a_stored_report_must_match_the_current_snapshot(record, report):
    data = record(report(snapshot=OLD))
    assert rejection(validate_records, stored(data)) == (
        "STALE report: snapshot differs; reverify current content"
    )


def test_a_stored_report_must_be_filed_under_its_own_role(record, report):
    data = record()
    data["reports"]["spec"] = report("behavioral")
    assert rejection(validate_records, stored(data)) == (
        "Stored reviewer role differs from report"
    )


@pytest.mark.parametrize(
    "check",
    [
        {"command": ["make", "check"], "exit_code": 0, "stdout": ""},
        {**passed(["make", "check"]), "exit_code": "0"},
        {**passed(["make", "check"]), "exit_code": True},
        {**passed(["make", "check"]), "stdout": None},
        {**passed(["make", "check"]), "stderr": 1},
        ["make", "check"],
    ],
)
def test_invalid_recorded_check_results_are_rejected(record, check):
    data = record(checks=[check])
    assert rejection(validate_records, stored(data)) == (
        "Invalid recorded command result"
    )


@pytest.mark.parametrize(
    "command,message",
    [
        ([], "recorded command: expected a list"),
        ("make check", "recorded command: expected a list"),
        (["make", ""], "recorded command: expected nonempty strings"),
    ],
)
def test_invalid_recorded_commands_are_rejected(record, command, message):
    data = record(checks=[passed(command)])
    assert rejection(validate_records, stored(data)) == message


def test_no_recorded_checks_is_a_valid_record(record):
    validate_records(stored(record(checks=[])))


# Carried history


def test_carried_reports_matching_their_history_are_accepted(record, report):
    old = record(report("spec", snapshot=OLD), report(snapshot=OLD), snapshot=OLD)
    current = record(
        carried(report("spec")), carried(report()), previous_evidence=HISTORY
    )
    validate_records(stored(current, previous(old)))


def test_successive_carries_are_accepted_through_the_whole_history(record, report):
    first = "2" * 64
    oldest = record(report(snapshot=OLD), snapshot=OLD)
    middle = record(
        carried(report(snapshot=first)),
        snapshot=first,
        previous_evidence="older.json",
    )
    middle["reports"]["behavioral"]["snapshot"] = first
    current = record(carried(report(), first), previous_evidence=HISTORY)
    validate_records(stored(current, previous(middle), previous(oldest, "older.json")))


def test_a_carried_report_requires_previous_evidence(record, report):
    data = record(carried(report()))
    assert rejection(validate_records, stored(data)) == (
        "Carried report requires previous evidence"
    )


def test_unavailable_history_requires_fresh_proof(record, report):
    data = record(carried(report()), previous_evidence=HISTORY)
    assert rejection(validate_records, stored(data, StoredRecord(HISTORY, None))) == (
        "Carried evidence history is unavailable; prepare again for fresh proof"
    )


def test_cyclic_history_is_rejected(record, report):
    data = record(carried(report()), previous_evidence=HISTORY)
    assert rejection(
        validate_records, stored(data, StoredRecord(HISTORY, None, cyclic=True))
    ) == ("Invalid cyclic verification history; prepare fresh evidence")


def test_invalid_history_is_rejected_like_a_stored_record(record, report):
    old = record(report(snapshot=OLD), snapshot=OLD, schema_version=2)
    data = record(carried(report()), previous_evidence=HISTORY)
    assert rejection(validate_records, stored(data, previous(old))) == (
        "Invalid or unsupported verification record; prepare again"
    )


@pytest.mark.parametrize(
    "tamper",
    [
        lambda report: report.update(summary="unreviewed replacement"),
        lambda report: report.update(carried_from="3" * 64),
        lambda report: report.update(verdict="FAIL"),
    ],
)
def test_carried_reports_that_differ_from_history_are_rejected(record, report, tamper):
    old = record(report(snapshot=OLD), snapshot=OLD)
    current = record(carried(report()), previous_evidence=HISTORY)
    tamper(current["reports"]["behavioral"])
    assert rejection(validate_records, stored(current, previous(old))) == (
        "Carried report differs from previous evidence"
    )


def test_a_carried_role_absent_from_history_is_rejected(record, report):
    old = record(report("spec", snapshot=OLD), snapshot=OLD)
    current = record(carried(report()), previous_evidence=HISTORY)
    assert rejection(validate_records, stored(current, previous(old))) == (
        "Carried report differs from previous evidence"
    )


# Schema compatibility


@pytest.mark.parametrize("version", [1, 2, 3])
def test_known_schemas_are_preserved_or_reused(version):
    reject_unsupported_schema({"schema_version": version})


def test_no_stored_record_needs_no_compatibility():
    reject_unsupported_schema(None)


@pytest.mark.parametrize("version", [999, 0, "3", None, True])
def test_unknown_schemas_need_compatible_tooling(version):
    assert rejection(reject_unsupported_schema, {"schema_version": version}) == (
        "Unsupported verification schema; use compatible tooling or archive the "
        "record before prepare again"
    )


# Staleness


def facts(data, token=TOKEN, **inputs):
    """Evidence facts for the stored record and the current snapshot."""
    return EvidenceFacts(
        token=token,
        inputs=frozen_json({**data["inputs"], **inputs}),
        records=stored(frozen_json(data)),
    )


def test_identical_snapshot_and_inputs_are_current(record):
    assert not stale(facts(record()))


def test_a_moved_comparison_tip_with_the_same_merge_base_is_current(record):
    assert not stale(facts(record(), base_tip="e" * 40))


def test_a_different_snapshot_is_stale(record):
    assert stale(facts(record(), token=OLD))


@pytest.mark.parametrize(
    "changes",
    [
        {"files": {"app.txt": {"sha256": "a" * 64, "executable": False}}},
        {"base": "e" * 40},
        {"tools": []},
        {"runtime": "3.13.0"},
        {"root": "/elsewhere"},
        {"starter_source": {"commit": "a" * 40}},
    ],
)
def test_changed_identity_inputs_are_stale(record, changes):
    assert stale(facts(record(), **changes))


# Admitting a new report


def test_a_report_from_a_fresh_session_is_admitted(record, report):
    admit(facts(record(report("standards"))), report("spec"))


def test_a_reviewer_filing_a_second_role_is_refused(record, report):
    data = record(report("standards", reviewer="one-session"))
    assert rejection(
        admit, facts(data), report("security", reviewer="one-session")
    ) == (
        "Independent roles require separate fresh sessions: "
        "{'one-session': ['security', 'standards']}"
    )


def test_replacing_a_role_report_is_not_sharing(record, report):
    data = record(report("standards", reviewer="one-session"))
    admit(facts(data), report("standards", reviewer="one-session", verdict="FAIL"))


@pytest.mark.parametrize(
    "checks",
    [
        [],
        [passed(["make", "check"], exit_code=2)],
        [passed(["make", "lint"])],
        [passed(["make", "check"]), passed(["make", "lint"])],
    ],
)
def test_behavioral_pass_requires_successful_planned_checks(record, report, checks):
    assert rejection(admit, facts(record(checks=checks)), report()) == (
        "Behavioral PASS requires successful recorded authoritative checks"
    )


@pytest.mark.parametrize(
    "role,verdict", [("behavioral", "FAIL"), ("standards", "PASS")]
)
def test_other_reports_need_no_recorded_checks(record, report, role, verdict):
    admit(facts(record(checks=[])), report(role, verdict=verdict))


def test_behavioral_pass_with_planned_checks_is_admitted(record, report):
    admit(facts(record()), report())


# Outcome and completeness

ORDINARY = ("standards", "spec", "behavioral")


def complete(record, report, tier="ordinary", **changes):
    roles = ORDINARY + (("security",) if tier == "sensitive" else ())
    if tier == "documentation":
        roles = ("behavioral",)
    return record(*(report(role) for role in roles), tier=tier, **changes)


@pytest.mark.parametrize("tier", ["documentation", "ordinary", "sensitive"])
def test_every_required_role_and_check_passes(record, report, tier):
    result = outcome(complete(record, report, tier))
    assert result["status"] == "PASS"
    assert result["missing"] == [] and result["missing_roles"] == []
    assert result["handoff"] == ""
    assert result["tier"] == tier


def test_missing_roles_are_incomplete_with_a_fresh_reviewer_handoff(record, report):
    result = outcome(record(report("behavioral"), tier="sensitive"))
    assert result["status"] == "INCOMPLETE"
    assert result["required_roles"] == ["standards", "spec", "behavioral", "security"]
    assert result["missing_roles"] == ["standards", "spec", "security"]
    assert result["missing"] == ["standards", "spec", "security"]
    assert result["shared_reviewers"] == {}
    assert result["handoff"] == (
        "Fresh read-only reviewer: inspect the plan requirement and actual scope; "
        "record missing roles. No implementer self-review. " + SESSIONS["sensitive"]
    )


@pytest.mark.parametrize("tier", ["documentation", "ordinary", "sensitive"])
def test_the_handoff_names_the_tier_session_rule(record, tier):
    assert outcome(record(tier=tier))["handoff"].endswith(SESSIONS[tier])


@pytest.mark.parametrize(
    "checks",
    [[], [passed(["make", "lint"])], [passed(["make", "check"])] * 2],
)
def test_unplanned_or_missing_checks_are_incomplete(record, report, checks):
    result = outcome(complete(record, report, checks=checks))
    assert result["status"] == "INCOMPLETE"
    assert result["missing"] == ["authoritative checks"]


def test_shared_reviewers_are_incomplete_even_with_every_role(record, report):
    data = complete(record, report)
    data["reports"]["spec"]["reviewer"] = "one-session"
    data["reports"]["standards"]["reviewer"] = "one-session"
    result = outcome(data)
    assert result["status"] == "INCOMPLETE"
    assert result["missing_roles"] == []
    assert result["shared_reviewers"] == {"one-session": ["spec", "standards"]}
    assert result["missing"] == [
        "separate sessions for independent review: "
        "{'one-session': ['spec', 'standards']}"
    ]


@pytest.mark.parametrize("verdict", ["FAIL", "CONCERNS"])
def test_a_non_passing_verdict_fails_even_when_incomplete(record, report, verdict):
    result = outcome(record(report("spec", verdict=verdict)))
    assert result["status"] == "FAIL"
    assert result["missing_roles"] == ["standards", "behavioral"]


def test_a_failed_check_fails(record, report):
    data = complete(record, report, checks=[passed(["make", "check"], 7)])
    assert outcome(data)["status"] == "FAIL"


def test_carried_reports_hand_checks_to_the_implementer(record, report):
    data = record(carried(report("spec")), checks=[], previous_evidence=HISTORY)
    result = outcome(data)
    assert result["status"] == "INCOMPLETE"
    assert result["handoff"] == (
        "Carried reports: the implementer may run verify check for this snapshot. "
        "Missing roles still require fresh independent review. "
    )
    assert result["previous_evidence"] == HISTORY


def test_the_outcome_reports_the_record_and_its_meaning(record, report):
    data = complete(
        record,
        report,
        check_checkout="checks/checkout",
        history_note="Previous evidence was not reused: reason",
    )
    data["inputs"]["starter_source"] = {"commit": "a" * 40, "manifest": {}}
    result = outcome(data)
    assert result["snapshot"] == TOKEN
    assert result["checkout"] == data["checkout"]
    assert result["check_checkout"] == "checks/checkout"
    assert result["history_note"] == "Previous evidence was not reused: reason"
    assert result["starter_source"] == {"commit": "a" * 40}
    assert result["tier_reason"] == "Fixture tier"
    assert result["floor"] == "ordinary"
    assert result["reports"] == data["reports"]
    assert result["checks"] == data["checks"]
    assert result["meaning"] == (
        "Recorded verification evidence only; not human acceptance or publication "
        "authorization."
    )

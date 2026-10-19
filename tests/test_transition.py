"""Exercise external adoption against a real archived starter installation."""

import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = "452d825ae58ad93d3ba66befedaacc30aa20318e"


def run(*args, cwd=ROOT):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True)


def legacy(tmp_path):
    target = tmp_path / "app"
    target.mkdir()
    archive = tmp_path / "legacy.tar"
    subprocess.run(
        ["git", "archive", "--output", str(archive), ARCHIVE], cwd=ROOT, check=True
    )
    with tarfile.open(archive) as tar:
        tar.extractall(target, filter="data")
    (target / "src").mkdir()
    (target / "src/app.js").write_text('console.log("application unchanged");\n')
    (target / "CLAUDE.md").write_text(
        (target / "CLAUDE.md").read_text() + "\nTeam rule: retain audit logs.\n"
    )
    run("git", "init", "-q", cwd=target)
    # Fixture commits must finish without background repacking racing read-only checks.
    run("git", "config", "gc.auto", "0", cwd=target)
    run("git", "config", "maintenance.auto", "false", cwd=target)
    run("git", "add", ".", cwd=target)
    run(
        "git",
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "baseline",
        cwd=target,
    )
    return target


def cli(*args):
    return run(sys.executable, str(ROOT / "agentic"), *map(str, args))


def test_minimal_preview_apply_preserves_application(tmp_path):
    target = legacy(tmp_path)
    before = run("git", "status", "--porcelain", cwd=target).stdout
    preview = cli("adopt", target, "--minimal")
    assert preview.returncode == 0, preview.stderr + preview.stdout
    assert run("git", "status", "--porcelain", cwd=target).stdout == before
    assert "DELETE" in preview.stdout
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = cli("adopt", target, "--minimal", "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr + applied.stdout
    assert (
        target / "src/app.js"
    ).read_text() == 'console.log("application unchanged");\n'
    assert "Team rule: retain audit logs." in (target / "CLAUDE.md").read_text()
    assert not (target / ".claude/commands/ship.md").exists()
    assert not (target / ".engineering/engineering/verification.py").exists()
    assert (target / ".claude/hooks/pre_tool_env_guard.py").exists()
    assert "verify check" not in (target / "CLAUDE.md").read_text()
    repeat = cli("adopt", target, "--minimal", "--apply")
    assert repeat.returncode == 0, repeat.stderr + repeat.stdout
    assert "No changes" in repeat.stdout


def test_customized_policy_is_conflict_without_writes(tmp_path):
    target = legacy(tmp_path)
    policy = target / "CLAUDE.md"
    policy.write_text(
        policy.read_text().replace("## Read first", "## Team custom rule")
    )
    result = cli("adopt", target, "--minimal", "--apply", "--expect", "stale")
    assert result.returncode == 1
    assert "customized integration" in result.stdout
    assert (target / ".engineering/engineering/verification.py").exists()
    assert not (target / ".agentic-setup").exists()


def test_stale_preview_preserves_new_edits(tmp_path):
    target = legacy(tmp_path)
    preview = cli("adopt", target, "--minimal")
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    policy = target / "CLAUDE.md"
    policy.write_text(policy.read_text() + "\nNew project rule\n")
    result = cli("adopt", target, "--minimal", "--apply", "--expect", token)
    assert result.returncode == 1
    assert "Stale preview" in result.stderr
    assert "New project rule" in policy.read_text()
    assert not (target / ".agentic-setup").exists()


def test_nested_instructions_and_team_ci_conflict(tmp_path):
    target = legacy(tmp_path)
    (target / "src/AGENTS.md").write_text(
        "Run engineering verify check before finishing.\n"
    )
    result = cli("adopt", target, "--minimal")
    assert result.returncode == 1
    assert "CONFLICT src/AGENTS.md" in result.stdout


def test_symlink_scope_is_refused(tmp_path):
    target = legacy(tmp_path)
    path = target / "CLAUDE.md"
    path.unlink()
    outside = tmp_path / "outside.md"
    outside.write_text("Do not overwrite me\n")
    path.symlink_to(outside)
    result = cli("adopt", target, "--minimal")
    assert result.returncode == 1
    assert "Symlink refused" in result.stderr
    assert outside.read_text() == "Do not overwrite me\n"


def test_unrelated_staged_and_unstaged_work_survives(tmp_path):
    target = legacy(tmp_path)
    app = target / "src/app.js"
    app.write_text("staged\n")
    run("git", "add", "src/app.js", cwd=target)
    app.write_text("unstaged\n")
    preview = cli("adopt", target, "--minimal")
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    result = cli("adopt", target, "--minimal", "--apply", "--expect", token)
    assert result.returncode == 0, result.stderr
    assert app.read_text() == "unstaged\n"
    assert run("git", "show", ":src/app.js", cwd=target).stdout == "staged\n"


def test_generic_init_and_selective_update(tmp_path):
    target = tmp_path / "new-project"
    result = cli("init", target)
    assert result.returncode == 0, result.stderr
    assert not (target / "pyproject.toml").exists()
    assert not (target / "engineering").exists()
    assert not (target / "tests").exists()
    assert cli("init", target).returncode == 1
    run("git", "init", "-q", cwd=target)
    run("git", "add", ".", cwd=target)
    run(
        "git",
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "init",
        cwd=target,
    )
    (target / "app.js").write_text("application progress\n")
    guidance = target / "docs/agents/explanation.md"
    guidance.write_text(guidance.read_text() + "\nTeam example: invoices.\n")
    result = cli(
        "update",
        target,
        "--only",
        "explanation",
        "--source-ref",
        run("git", "rev-parse", "HEAD").stdout.strip(),
    )
    assert result.returncode == 0, result.stderr
    assert "No changes" in result.stdout
    assert "Team example: invoices." in guidance.read_text()
    assert (target / "app.js").read_text() == "application progress\n"


def test_native_application_work_and_revert_preserve_later_change(tmp_path):
    target = legacy(tmp_path)
    app = target / "src/app.py"
    app.write_text('print("native application works")\n')
    run("git", "add", "src/app.py", cwd=target)
    identity = ["-c", "user.name=Test", "-c", "user.email=test@example.invalid"]
    run("git", *identity, "commit", "-qm", "native app baseline", cwd=target)
    preview = cli("adopt", target, "--minimal")
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    import shlex

    command = shlex.join([sys.executable, "src/app.py"])
    result = cli(
        "adopt", target, "--minimal", "--apply", "--expect", token, "--check", command
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.count("native application works") == 2
    run("git", "add", "-A", cwd=target)
    run("git", *identity, "commit", "-qm", "minimal transition", cwd=target)
    transition = run("git", "rev-parse", "HEAD", cwd=target).stdout.strip()
    app.write_text('print("later feature works")\n')
    run("git", "add", "src/app.py", cwd=target)
    run("git", *identity, "commit", "-qm", "application feature", cwd=target)
    assert (
        run(sys.executable, "src/app.py", cwd=target).stdout == "later feature works\n"
    )
    reverted = run("git", *identity, "revert", "--no-edit", transition, cwd=target)
    assert reverted.returncode == 0, reverted.stderr
    assert (target / ".engineering/engineering/verification.py").exists()
    assert (
        run(sys.executable, "src/app.py", cwd=target).stdout == "later feature works\n"
    )


def test_locally_deleted_tracked_guidance_is_not_recreated(tmp_path):
    target = legacy(tmp_path)
    (target / "CLAUDE.md").unlink()
    preview = cli("adopt", target, "--minimal")
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    result = cli("adopt", target, "--minimal", "--apply", "--expect", token)
    assert result.returncode == 1
    assert "local edits" in result.stderr
    assert not (target / "CLAUDE.md").exists()


def test_initialize_refuses_symlinked_parent(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "alias"
    link.symlink_to(real, target_is_directory=True)
    result = cli("init", link / "new-app")
    assert result.returncode == 1
    assert not (real / "new-app").exists()


def test_brownfield_reuses_named_standards_and_discovers_native_scripts(tmp_path):
    target = tmp_path / "web"
    (target / "docs/team").mkdir(parents=True)
    (target / "docs/team/style-guide.md").write_text(
        "# Coding guidelines\n\nTest public behavior.\n"
    )
    (target / "package.json").write_text(
        '{"scripts":{"test":"node --test","lint":"eslint ."}}\n'
    )
    (target / "pnpm-lock.yaml").write_text("lockfileVersion: 9\n")
    run("git", "init", "-q", cwd=target)
    run("git", "add", ".", cwd=target)
    run(
        "git",
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "web app",
        cwd=target,
    )
    preview = cli("adopt", target)
    assert preview.returncode == 0, preview.stderr
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = cli("adopt", target, "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr
    assert not (target / "CODING_STANDARDS.md").exists()
    assert (
        "docs/team/style-guide.md" in (target / "docs/agents/workflow.md").read_text()
    )
    assert "pnpm run test" in (target / "docs/agents/checks.md").read_text()
    assert not (target / "pyproject.toml").exists()

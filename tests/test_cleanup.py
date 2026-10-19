"""Bounded archival through the public CLI, using disposable projects."""

from test_transition import cli, run


def project(tmp_path):
    target = tmp_path / "app"
    target.mkdir()
    run("git", "init", cwd=target)
    run("git", "config", "user.email", "test@example.com", cwd=target)
    run("git", "config", "user.name", "Test", cwd=target)
    (target / "app.txt").write_text("application\n")
    (target / ".gitignore").write_text("/.engineering/state/verification/\n.venv/\n")
    run("git", "add", ".", cwd=target)
    run("git", "commit", "-m", "baseline", cwd=target)
    old = target / ".engineering"
    old.mkdir()
    (old / "config.toml").write_text("custom = true\n")
    (old / "python").symlink_to("/missing/python")
    notes = target / ".scratch/agentic-setup-adoption"
    notes.mkdir(parents=True)
    (notes / "spec.md").write_text("old migration\n")
    return target


def test_cleanup_previews_then_archives_without_touching_application(tmp_path):
    target = project(tmp_path)
    archive = tmp_path / "archive"
    args = ["cleanup", target, "--adoption-notes", "--archive", archive]
    report = tmp_path / "preview.html"
    preview = cli(*args, "--html", report)
    assert preview.returncode == 0, preview.stderr
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    assert (target / ".engineering/config.toml").exists()
    assert not archive.exists()
    assert "Archive" in report.read_text()
    applied = cli(*args, "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr
    assert not (target / ".engineering").exists()
    assert not (target / ".scratch/agentic-setup-adoption").exists()
    saved = archive / token
    assert (saved / ".engineering/config.toml").read_text() == "custom = true\n"
    assert (saved / ".engineering/python").is_symlink()
    assert (
        saved / ".scratch/agentic-setup-adoption/spec.md"
    ).read_text() == "old migration\n"
    assert (saved / "gitignore.before").read_text().startswith("/.engineering/")
    assert (target / ".gitignore").read_text() == ".venv/\n"
    assert (target / "app.txt").read_text() == "application\n"
    repeat = cli(*args, "--apply", "--expect", token)
    assert repeat.returncode == 0 and "No changes" in repeat.stdout
    assert list(archive.iterdir()) == [saved]


def test_cleanup_refuses_active_legacy_callers(tmp_path):
    target = project(tmp_path)
    (target / "Makefile").write_text("check:\n\t./engineering verify\n")
    result = cli("cleanup", target, "--archive", tmp_path / "archive")
    assert result.returncode != 0 and "retired wiring" in result.stderr
    assert (target / ".engineering/config.toml").exists()


def test_changed_tree_rejects_old_token_and_preserves_unrelated_dirty_work(tmp_path):
    target = project(tmp_path)
    archive = tmp_path / "archive"
    args = ["cleanup", target, "--archive", archive]
    preview = cli(*args)
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    (target / ".engineering/new").write_text("arrived later")
    result = cli(*args, "--apply", "--expect", token)
    assert result.returncode != 0 and "Stale" in result.stderr
    assert not archive.exists()
    (target / "app.txt").write_text("uncommitted application edit")
    preview = cli(*args)
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    result = cli(*args, "--apply", "--expect", token)
    assert result.returncode == 0, result.stderr
    assert (target / "app.txt").read_text() == "uncommitted application edit"
    assert (target / ".scratch/agentic-setup-adoption/spec.md").exists()


def test_unsafe_paths_and_nested_git_are_refused(tmp_path):
    target = project(tmp_path)
    for archive in [target / "archive", target.parent, tmp_path / ".git/archive"]:
        result = cli("cleanup", target, "--archive", archive)
        assert result.returncode != 0
    (target / ".engineering/.git").write_text("gitdir: /somewhere")
    result = cli("cleanup", target, "--archive", tmp_path / "archive")
    assert result.returncode != 0 and "Nested Git" in result.stderr
    assert (target / ".engineering/config.toml").exists()


def test_symlink_root_is_refused_and_html_cannot_apply(tmp_path):
    target = project(tmp_path)
    (target / ".engineering").rename(tmp_path / "outside")
    (target / ".engineering").symlink_to(tmp_path / "outside", target_is_directory=True)
    result = cli("cleanup", target, "--archive", tmp_path / "archive")
    assert result.returncode != 0 and "Symlink" in result.stderr
    result = cli("cleanup", target, "--apply", "--html", tmp_path / "report.html")
    assert result.returncode != 0 and "preview-only" in result.stderr
    assert (tmp_path / "outside/config.toml").exists()


def test_failed_second_move_rolls_back_first(tmp_path, monkeypatch, capsys):
    import sys
    from pathlib import Path

    from agentic_setup.cli import main

    target = project(tmp_path)
    archive = tmp_path / "archive"
    args = [
        "agentic",
        "cleanup",
        str(target),
        "--adoption-notes",
        "--archive",
        str(archive),
    ]
    monkeypatch.setattr(sys, "argv", args)
    assert main() == 0
    token = capsys.readouterr().out.split("PREVIEW ")[1].splitlines()[0]
    original = Path.rename

    def fail_notes(path, destination):
        if path == target / ".scratch/agentic-setup-adoption":
            raise OSError("injected move failure")
        return original(path, destination)

    monkeypatch.setattr(Path, "rename", fail_notes)
    monkeypatch.setattr(sys, "argv", args + ["--apply", "--expect", token])
    assert main() == 1
    assert "rolled back" in capsys.readouterr().err
    assert (target / ".engineering/config.toml").read_text() == "custom = true\n"
    assert (target / ".engineering/python").is_symlink()
    assert (target / ".scratch/agentic-setup-adoption/spec.md").exists()
    assert (target / ".gitignore").read_text().startswith("/.engineering/")
    assert (archive / token / "manifest.json").exists()


def test_cleanup_refuses_imports_into_archived_folders(tmp_path):
    target = project(tmp_path)
    (target / ".engineering/custom.md").write_text("Keep project rules")
    for reference in [
        "@.engineering/custom.md",
        "[notes](.scratch/agentic-setup-adoption/spec.md)",
    ]:
        (target / "CLAUDE.md").write_text(reference)
        result = cli(
            "cleanup", target, "--adoption-notes", "--archive", tmp_path / "archive"
        )
        assert result.returncode != 0 and "reference" in result.stderr
        assert (target / ".engineering/custom.md").exists()
        assert not (tmp_path / "archive").exists()


def test_standalone_verification_checkout_is_archived_intact(tmp_path):
    target = project(tmp_path)
    checkout = target / ".engineering/state/verification/old-run/checkout"
    checkout.mkdir(parents=True)
    run("git", "init", cwd=checkout)
    archive = tmp_path / "archive"
    args = ["cleanup", target, "--archive", archive]
    preview = cli(*args)
    assert preview.returncode == 0, preview.stderr
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = cli(*args, "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr
    assert (archive / token / checkout.relative_to(target) / ".git/HEAD").is_file()


def test_manifest_failure_rolls_back_ignore_edit_and_never_reads_secrets(
    tmp_path, monkeypatch, capsys
):
    import sys
    from pathlib import Path

    from agentic_setup.cli import main

    target = project(tmp_path)
    secret = target / ".engineering/.env"
    secret.write_text("fixture secret")
    (target / ".gitignore").chmod(0o640)
    archive = tmp_path / "archive"
    args = ["agentic", "cleanup", str(target), "--archive", str(archive)]
    original_read = Path.read_bytes
    original_write = Path.write_bytes

    def guard_read(path):
        assert path.name != ".env", "Secret file was read"
        return original_read(path)

    def fail_manifest(path, content):
        if path.name == "manifest.json" and b'"applied"' in content:
            raise OSError("injected completion failure")
        return original_write(path, content)

    monkeypatch.setattr(Path, "read_bytes", guard_read)
    monkeypatch.setattr(sys, "argv", args)
    assert main() == 0
    token = capsys.readouterr().out.split("PREVIEW ")[1].splitlines()[0]
    monkeypatch.setattr(Path, "write_bytes", fail_manifest)
    monkeypatch.setattr(sys, "argv", args + ["--apply", "--expect", token])
    assert main() == 1
    assert "rolled back" in capsys.readouterr().err
    assert secret.exists()
    assert (
        target / ".gitignore"
    ).read_text() == "/.engineering/state/verification/\n.venv/\n"
    assert (target / ".gitignore").stat().st_mode & 0o777 == 0o640


def test_linked_snapshot_repository_is_refused(tmp_path):
    target = project(tmp_path)
    checkout = target / ".engineering/state/verification/old-run/checkout"
    checkout.mkdir(parents=True)
    run("git", "init", cwd=checkout)
    alternates = checkout / ".git/objects/info/alternates"
    alternates.write_text("/missing/objects\n")
    result = cli("cleanup", target, "--archive", tmp_path / "archive")
    assert result.returncode != 0 and "Linked snapshot" in result.stderr
    assert alternates.exists()

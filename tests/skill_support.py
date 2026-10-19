"""Disposable fixtures and an explicit external npm process double."""

import os
import sys
from pathlib import Path

import pytest
from test_transition import run
from test_updates import commit


@pytest.fixture
def installer(tmp_path, monkeypatch):
    folder = tmp_path / "bin"
    folder.mkdir()
    script = folder / "npx"
    script.write_text(
        f"#!{sys.executable}\n"
        + """
import sys, os, json, shutil, hashlib
from pathlib import Path
args=sys.argv[1:]
assert args[:3]==['--yes','--package=skills@1.7.2','skills'], args
assert args[3]=='add', args
source=Path(args[4]); names=args[args.index('--skill')+1:args.index('--agent')]
root=Path.cwd()
lock_path=root/'skills-lock.json'
lock=json.loads(lock_path.read_text()) if lock_path.exists() else {'version':1,'skills':{}}
for name in names:
    incoming=source/'skills'/name
    if not incoming.is_dir(): sys.exit(2)
    dest=root/'.agents/skills'/name
    if dest.exists(): shutil.rmtree(dest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(incoming,dest)
    alias=root/'.claude/skills'/name
    if alias.is_symlink(): alias.unlink()
    elif alias.exists(): shutil.rmtree(alias)
    alias.parent.mkdir(parents=True,exist_ok=True)
    alias.symlink_to('../../.agents/skills/'+name)
    lock['skills'][name]={'source':os.path.relpath(source,root),'sourceType':'local','skillPath':'skills/'+name+'/SKILL.md','computedHash':hashlib.sha256((incoming/'SKILL.md').read_bytes()).hexdigest()}
lock_path.write_text(json.dumps(lock,indent=2)+'\\n')
print(json.dumps([{'name':n,'status':'installed'} for n in names]))
"""
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", str(folder) + os.pathsep + os.environ["PATH"])
    return script


def source_repo(tmp_path):
    source = tmp_path / "source"
    skill = source / "skills/show-me"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: show-me\ndescription: Test presentation\n---\nUpstream presentation\n"
    )
    (skill / "support.md").write_text("Upstream support\n")
    run("git", "init", "-q", cwd=source)
    revision = commit(source, "source")
    return source, skill, revision


def target_repo(tmp_path):
    target = tmp_path / "app"
    target.mkdir()
    (target / "app.txt").write_text("Keep application\n")
    run("git", "init", "-q", cwd=target)
    commit(target, "baseline")
    return target


def saved_plan(result):
    assert result.returncode == 0, result.stderr + result.stdout
    return Path(result.stdout.split("PLAN ")[1].splitlines()[0]), result.stdout.split(
        "PREVIEW "
    )[1].splitlines()[0]

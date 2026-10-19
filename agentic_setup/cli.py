"""Small external installer command line."""

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

from .adopt import plan_adoption
from .cleanup import run_cleanup
from .files import baseline, checked_root
from .freshness import check_skills
from .inspection import inspect_target
from .preview import next_report, report_destination, write_preview
from .setup import SCOPES, initialize, plan_update
from .skills import BUNDLES, plan_skills
from .sources import skill_source


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="agentic",
        description="Agentic Setup: configure target workspaces with development conventions and skills",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser(
        "inspect", help="read-only setup and convention report"
    )
    inspect.add_argument("target", type=Path)
    adopt = commands.add_parser("adopt")
    adopt.add_argument("target", type=Path)
    adopt.add_argument("--minimal", action="store_true")
    adopt.add_argument(
        "--resolutions", type=Path, help="explicit external project resolution plan"
    )
    adopt.add_argument(
        "--html",
        nargs="?",
        const="auto",
        help="save HTML; default: migrations/<workspace>/preview-NNN.html",
    )
    adopt.add_argument("--apply", action="store_true")
    adopt.add_argument(
        "--check", help="explicit native command to run before and after apply"
    )
    adopt.add_argument(
        "--expect", help="preview token; rejects changed content or source"
    )
    cleanup = commands.add_parser("cleanup", help="archive dormant legacy leftovers")
    cleanup.add_argument("target", type=Path)
    cleanup.add_argument("--adoption-notes", action="store_true")
    cleanup.add_argument("--archive", type=Path)
    cleanup.add_argument("--html", nargs="?", const="auto")
    cleanup.add_argument("--apply", action="store_true")
    cleanup.add_argument("--expect")
    init = commands.add_parser("init")
    init.add_argument("target", type=Path)
    init.add_argument("--python-seed", action="store_true")
    update = commands.add_parser("update")
    update.add_argument("target", type=Path)
    update.add_argument("--only", choices=SCOPES, required=True)
    update.add_argument(
        "--html",
        nargs="?",
        const="auto",
        help="save HTML; default: migrations/<workspace>/preview-NNN.html",
    )
    update.add_argument("--source-ref", required=True)
    update.add_argument("--apply", action="store_true")
    update.add_argument("--expect")
    skills_group = commands.add_parser("skills")
    skill_commands = skills_group.add_subparsers(dest="skill_command", required=True)
    skill_check = skill_commands.add_parser(
        "check", help="read-only online revision check"
    )
    skill_check.add_argument("target", type=Path)
    skill_check.add_argument("--bundle", choices=BUNDLES)
    for operation in ("install", "update"):
        skills = skill_commands.add_parser(operation)
        skills.add_argument("target", type=Path)
        skills.add_argument(
            "--from",
            dest="checkout",
            type=Path,
            help="explicit clean local checkout; no fetching",
        )
        skills.add_argument(
            "--ref",
            help="full upstream commit hash; defaults to latest default-branch HEAD",
        )
        skills.add_argument("--bundle", choices=BUNDLES, default="matt")
        skills.add_argument(
            "--html",
            nargs="?",
            const="auto",
            help="save HTML; default: migrations/<workspace>/preview-NNN.html",
        )
        skills.add_argument("--apply", action="store_true")
        skills.add_argument("--expect")
    args = parser.parse_args()
    try:
        html_path = getattr(args, "html", None)
        if html_path is not None:
            if args.apply:
                raise ValueError("--html is preview-only; omit --apply")
            if html_path != "auto":
                html_path = report_destination(Path(html_path), args.target)
        if args.command == "cleanup":
            return run_cleanup(
                args.target,
                args.archive,
                args.adoption_notes,
                html_path,
                args.apply,
                args.expect,
            )
        if args.command == "skills" and args.skill_command == "check":
            report, status = check_skills(args.target, args.bundle)
            print(report)
            return status
        if args.command == "inspect":
            print(inspect_target(args.target))
            return 0
        if args.command == "init":
            initialize(args.target, args.python_seed)
            print(
                "Initialized configuration. Install selected skills, then run /setup-matt-pocock-skills to confirm missing setup choices."
            )
            return 0
        if args.command == "adopt":
            plan = plan_adoption(args.target, args.minimal, args.resolutions)
        elif args.command == "skills":
            target = checked_root(args.target)
            baseline(target)  # Reject invalid targets before any network activity.
            with skill_source(
                BUNDLES[args.bundle][0], args.checkout, args.ref
            ) as checkout:
                plan = plan_skills(
                    target, checkout, args.bundle, update=args.skill_command == "update"
                )
        else:
            plan = plan_update(args.target, args.only, args.source_ref)
        for note in plan.notes:
            print(note)
        for conflict in plan.conflicts:
            print(f"CONFLICT {conflict}")
        print(f"PREVIEW {plan.token()}")
        if html_path is not None:
            if html_path == "auto":
                html_path = next_report(plan.root, getattr(args, "resolutions", None))
            write_preview(plan, html_path)
            print(f"HTML preview: {html_path}")
        if plan.conflicts:
            return 1
        if not plan.changes:
            print("No changes")
            return 0
        if args.apply:
            if not args.expect:
                raise ValueError(
                    "Apply requires --expect <PREVIEW token>; preview first"
                )
            check = getattr(args, "check", None)
            before = None
            if check:
                before = subprocess.run(shlex.split(check), cwd=plan.root).returncode
                print(f"Native baseline exit: {before}")
            plan.apply(args.expect)
            if check:
                after = subprocess.run(shlex.split(check), cwd=plan.root).returncode
                print(f"Native after exit: {after}; baseline: {before}")
                if after:
                    print(
                        "Transition applied; native verification failed. Inspect baseline and diff; do not claim verification."
                    )
                    return 1
            else:
                print("Native verification not run: no --check command supplied.")
            print(
                "Applied. Inspect git diff, run agreed native checks, and commit this transition separately. Roll back with git revert of that commit."
            )
        return 0
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

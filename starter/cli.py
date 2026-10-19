"""Small external installer command line."""

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

from .adopt import plan_adoption
from .setup import SCOPES, initialize, plan_update
from .skills import BUNDLES, plan_skills


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Explicit external starter installation; no daily runtime"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    adopt = commands.add_parser("adopt")
    adopt.add_argument("target", type=Path)
    adopt.add_argument("--minimal", action="store_true")
    adopt.add_argument("--apply", action="store_true")
    adopt.add_argument(
        "--check", help="explicit native command to run before and after apply"
    )
    adopt.add_argument(
        "--expect", help="preview token; rejects changed content or source"
    )
    init = commands.add_parser("init")
    init.add_argument("target", type=Path)
    init.add_argument("--python-seed", action="store_true")
    update = commands.add_parser("update")
    update.add_argument("target", type=Path)
    update.add_argument("--only", choices=SCOPES, required=True)
    update.add_argument("--source-ref", required=True)
    update.add_argument("--apply", action="store_true")
    update.add_argument("--expect")
    skills = commands.add_parser("skills")
    skills.add_argument("target", type=Path)
    skills.add_argument("--from", dest="checkout", type=Path, required=True)
    skills.add_argument("--bundle", choices=BUNDLES, default="matt")
    skills.add_argument("--apply", action="store_true")
    skills.add_argument("--expect")
    args = parser.parse_args()
    try:
        if args.command == "init":
            initialize(args.target, args.python_seed)
            print(
                "Initialized configuration. Install selected skills, then run /setup-matt-pocock-skills to confirm missing setup choices."
            )
            return 0
        if args.command == "adopt":
            plan = plan_adoption(args.target, args.minimal)
        elif args.command == "skills":
            plan = plan_skills(args.target, args.checkout, args.bundle)
        else:
            plan = plan_update(args.target, args.only, args.source_ref)
        for note in plan.notes:
            print(note)
        for conflict in plan.conflicts:
            print(f"CONFLICT {conflict}")
        print(f"PREVIEW {plan.token()}")
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

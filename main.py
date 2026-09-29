"""
Laptop Service Audit & Security Checker

A Windows defensive auditing tool that:
- Creates a pre-service baseline
- Captures system snapshots
- Compares snapshots against the baseline
- Detects added, removed, and modified system state
- Generates audit reports
- Verifies baseline integrity

Usage:
    python main.py
    python main.py baseline
    python main.py audit
    python main.py compare
    python main.py verify
    python main.py status
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from cli.commands import (
    compare_with_baseline,
    create_baseline,
    create_snapshot,
    ensure_directories,
    get_status,
    verify_baseline,
)
from cli.menu import main_menu


PROJECT_ROOT = Path(__file__).resolve().parent

BASELINE_DIR = PROJECT_ROOT / "baseline"
SNAPSHOTS_DIR = PROJECT_ROOT / "snapshots"
REPORTS_DIR = PROJECT_ROOT / "reports"

BASELINE_FILE = BASELINE_DIR / "baseline.json"
BASELINE_HASH_FILE = BASELINE_DIR / "baseline.sha256"


def automatic_mode():
    """
    Main one-command workflow.

    First run:
        Create baseline.

    Later runs:
        Capture snapshot and compare.
    """

    print()
    print("=" * 60)
    print("     LAPTOP SERVICE AUDIT & SECURITY CHECKER")
    print("=" * 60)
    print()

    if not BASELINE_FILE.exists():

        print("[i] No baseline detected.")
        print("[i] Creating official pre-service baseline.")

        create_baseline()

        return

    print("[i] Existing baseline detected.")
    print("[+] Running post-baseline audit.")

    timestamp_value = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")

    snapshot, _ = create_snapshot(timestamp_value)

    compare_with_baseline(
        snapshot
    )


def main():

    ensure_directories()

    parser = argparse.ArgumentParser(
        description=(
            "Windows defensive laptop "
            "service auditing tool."
        )
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=[
            "baseline",
            "audit",
            "compare",
            "verify",
            "status",
        ],
        help="Command to execute.",
    )

    args = parser.parse_args()

    if args.command is None:

        automatic_mode()

    elif args.command == "baseline":

        result = create_baseline()

        print()
        print("=" * 60)
        print("              BASELINE STATUS")
        print("=" * 60)
        print()

        if not result["success"]:
            print(f"[!] {result['message']}")
        else:
            print("[+] Baseline created successfully.")
            print(f"Baseline : {result['baseline_file']}")
            print(f"SHA-256  : {result['sha256']}")

        print()


    elif args.command == "audit":

        timestamp_value = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")

        _, snapshot_file = create_snapshot(timestamp_value)

        print()
        print("=" * 60)
        print("              SNAPSHOT CREATED")
        print("=" * 60)
        print()
        print(f"Snapshot: {snapshot_file}")
        print()

    elif args.command == "compare":

        timestamp_value = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")

        snapshot, snapshot_file = create_snapshot(timestamp_value)

        result = compare_with_baseline(
            snapshot,
            timestamp_value,
        )

        print()
        print("=" * 60)
        print("              AUDIT COMPARISON")
        print("=" * 60)
        print()

        if not result["success"]:
            print(f"[!] {result['message']}")
        else:
            summary = result["summary"]

            print(f"Added     : {summary['added']}")
            print(f"Removed   : {summary['removed']}")
            print(f"Modified  : {summary['modified']}")
            print(f"Unchanged : {summary['unchanged']}")
            print()
            print(f"Snapshot   : {snapshot_file}")
            print(f"JSON Report: {result['report_file']}")
            print(f"TXT Report : {result['text_report_file']}")
            print()

    elif args.command == "verify":

        result = verify_baseline()

        print()
        print("=" * 60)
        print("             BASELINE INTEGRITY")
        print("=" * 60)
        print()

        if not result["success"]:
            print(f"[!] {result['message']}")
        else:
            print(f"Expected: {result['expected_hash']}")
            print(f"Actual  : {result['actual_hash']}")
            print()

            if result["valid"]:
                print("[OK] Baseline integrity verified.")
            else:
                print("[ALERT] Baseline integrity FAILED.")

        print()

    elif args.command == "status":
        result = get_status()

        print()
        print("=" * 60)
        print("        LAPTOP SERVICE AUDIT STATUS")
        print("=" * 60)
        print()

        print(
            f"Baseline : "
            f"{'EXISTS' if result['baseline_exists'] else 'MISSING'}"
        )

        print(
            f"Hash     : "
            f"{'EXISTS' if result['hash_exists'] else 'MISSING'}"
        )

        print(
            f"Snapshots: {result['snapshot_count']}"
        )

        print(
            f"Reports  : {result['report_count']}"
        )

        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        main_menu()
    else:
        main()
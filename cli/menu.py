from datetime import datetime

from .commands import (
    compare_with_baseline,
    create_baseline,
    create_snapshot,
    ensure_directories,
    get_verifiable_evidence_files,
    get_verifiable_report_files,
    get_latest_report,
    get_status,
    verify_baseline,
    verify_evidence,
    verify_report,
)
from .display import (
    print_error,
    print_header,
    print_info,
    print_separator,
    print_success,
    print_warning,
)


def timestamp():
    """Return a filesystem-safe timestamp."""

    return datetime.now().astimezone().strftime(
        "%Y%m%d_%H%M%S"
    )


def run_full_audit():
    """Create a snapshot and compare it with the baseline."""

    print_info("Collecting current system state...")
    print_info("Please wait...")

    snapshot, snapshot_file, snapshot_hash = create_snapshot(timestamp())

    print_success("Snapshot created.")
    print_success(f"Saved to: {snapshot_file}")

    result = compare_with_baseline(
        snapshot,
        timestamp(),
    )

    if not result["success"]:
        print_warning(result["message"])
        return

    summary = result["summary"]

    print()
    print_header("AUDIT COMPARISON")

    print(f"Added     : {summary['added']}")
    print(f"Removed   : {summary['removed']}")
    print(f"Modified  : {summary['modified']}")
    print(f"Unchanged : {summary['unchanged']}")

    print()
    print_success(f"Report: {result['report_file']}")


def handle_baseline():
    """Handle baseline creation."""

    print_info("Collecting complete system baseline...")
    print_info("Please wait...")

    result = create_baseline()

    if not result["success"]:
        print_warning(result["message"])
        return

    print_success("Baseline created successfully.")
    print_success(f"SHA-256: {result['sha256']}")


def handle_snapshot():
    """Handle snapshot creation."""

    print_info("Collecting current system state...")
    print_info("Please wait...")

    _, snapshot_file, _ = create_snapshot(timestamp())

    print_success("Snapshot created.")
    print_success(f"Saved to: {snapshot_file}")


def handle_compare():
    """Create a snapshot and compare it with the baseline."""

    run_full_audit()


def handle_verify():
    """Handle baseline integrity verification."""

    result = verify_baseline()

    if not result["success"]:
        print_warning(result["message"])
        return

    print_header("BASELINE INTEGRITY")

    print(f"Expected: {result['expected_hash']}")
    print(f"Actual  : {result['actual_hash']}")
    print()

    if result["valid"]:
        print_success("Baseline integrity verified.")
    else:
        print_error("Baseline integrity FAILED.")

def handle_verify_evidence():
    """Handle evidence file integrity verification."""

    evidence_files = get_verifiable_evidence_files()

    if not evidence_files:
        print_warning("No evidence files found.")
        return

    print_header("SELECT EVIDENCE FILE")

    for index, evidence_file in enumerate(evidence_files, start=1):
        print(f"{index}. {evidence_file}")

    print()

    while True:
        choice = input(
            f"Select an evidence file [1-{len(evidence_files)}]: "
        ).strip()

        if choice.isdigit():
            index = int(choice)

            if 1 <= index <= len(evidence_files):
                evidence_file = evidence_files[index - 1]
                break

        print_error(
            f"Invalid option. Please select a number from 1 to {len(evidence_files)}."
        )

    result = verify_evidence(evidence_file)

    if not result["success"] and "actual_hash" not in result:
        print_warning(result["error"])
        return

    print_header("EVIDENCE INTEGRITY")

    print(f"File     : {result['file']}")
    print(f"Hash File: {result['hash_file']}")
    print(f"Expected : {result['expected_hash']}")
    print(f"Actual   : {result['actual_hash']}")
    print()

    if result["success"]:
        print_success("Evidence integrity verified.")
    else:
        print_error("Evidence integrity FAILED.")

def handle_verify_report():
    """Handle report file integrity verification."""

    report_files = get_verifiable_report_files()

    if not report_files:
        print_warning("No report files found.")
        return

    print_header("SELECT REPORT FILE")

    for index, report_file in enumerate(report_files, start=1):
        print(f"{index}. {report_file}")

    print()

    while True:
        choice = input(
            f"Select a report file [1-{len(report_files)}]: "
        ).strip()

        if choice.isdigit():
            index = int(choice)

            if 1 <= index <= len(report_files):
                report_file = report_files[index - 1]
                break

        print_error(
            f"Invalid option. Please select a number from 1 to {len(report_files)}."
        )

    result = verify_report(report_file)

    if not result["success"] and "actual_hash" not in result:
        print_warning(result["error"])
        return

    print_header("REPORT INTEGRITY")

    print(f"File     : {result['file']}")
    print(f"Hash File: {result['hash_file']}")
    print(f"Expected : {result['expected_hash']}")
    print(f"Actual   : {result['actual_hash']}")
    print()

    if result["success"]:
        print_success("Report integrity verified.")
    else:
        print_error("Report integrity FAILED.")

def handle_status():
    """Display audit project status."""

    status = get_status()

    print_header("SENTINELTRACE STATUS")

    print(
        f"Baseline : "
        f"{'EXISTS' if status['baseline_exists'] else 'MISSING'}"
    )

    print(
        f"Hash     : "
        f"{'EXISTS' if status['hash_exists'] else 'MISSING'}"
    )

    print(f"Snapshots: {status['snapshot_count']}")
    print(f"Reports  : {status['report_count']}")


def show_changes():
    """Display readable details from the latest audit report."""

    result = get_latest_report()

    if result is None:
        print_warning("No audit report found.")
        return

    report = result["report"]
    comparison = report.get("comparison", {})

    print_header("WHAT ARE THE CHANGES?")

    found_changes = False

    for section_name, section in comparison.items():

        modified = section.get("modified", [])
        added = section.get("added", [])
        removed = section.get("removed", [])

        if not modified and not added and not removed:
            continue

        found_changes = True

        print(section_name.upper())
        print_separator()

        for item in added:
            print(f"[ADDED] {item.get('id', item)}")

        for item in removed:
            print(f"[REMOVED] {item.get('id', item)}")

        for item in modified:
            item_id = item.get("id", "Unknown")

            print(f"[MODIFIED] {item_id}")

            before = item.get("before", {})
            after = item.get("after", {})

            if section_name == "services":
                print(
                    f"  Display Name : "
                    f"{after.get('DisplayName', before.get('DisplayName', 'N/A'))}"
                )

                before_state = before.get("State", "N/A")
                after_state = after.get("State", "N/A")

                if before_state != after_state:
                    print(
                        f"  State        : "
                        f"{before_state} -> {after_state}"
                    )
                else:
                    print(f"  State        : {after_state}")

                print(
                    f"  Start Mode   : "
                    f"{after.get('StartMode', before.get('StartMode', 'N/A'))}"
                )

                print(
                    f"  Account      : "
                    f"{after.get('StartName', before.get('StartName', 'N/A'))}"
                )

            elif section_name == "scheduled_tasks":
                print(
                    f"  Path         : "
                    f"{after.get('TaskPath', before.get('TaskPath', 'N/A'))}"
                )

                print(
                    f"  Author       : "
                    f"{after.get('Author', before.get('Author', 'N/A'))}"
                )

                before_triggers = before.get("Triggers", [])
                after_triggers = after.get("Triggers", [])

                if before_triggers != after_triggers:
                    print("  Trigger      : Schedule trigger changed")
                else:
                    print("  Trigger      : No trigger change")

            else:
                print(f"  Before       : {before}")
                print(f"  After        : {after}")

            print()

    if not found_changes:
        print_success("No changes detected in the latest report.")

    print()
    print_info(f"Report: {result['file']}")

def show_menu():
    """Display the main interactive menu."""

    print_header("SENTINELTRACE")

    print("1. Compare Changes")
    print("2. What Are the Changes?")
    print("3. Run Full Audit")
    print("4. Create Snapshot")
    print("5. Create Baseline")
    print("6. Verify Baseline Integrity")
    print("7. Verify Evidence Integrity")
    print("8. Verify Report Integrity")
    print("9. View Audit Status")
    print("10. View Latest Report")
    print("11. Exit")

    print_separator()


def get_choice():
    """Get and validate the user's menu selection."""

    while True:
        choice = input("Select an option [1-11]: ").strip()

        if choice in {str(number) for number in range(1, 12)}:
            return choice

        print_error(
            "Invalid option. Please select a number from 1 to 11."
        )


def main_menu():
    """Run the interactive CLI menu."""

    ensure_directories()

    while True:
        show_menu()

        choice = get_choice()

        print()

        if choice == "1":
            handle_compare()

        elif choice == "2":
            show_changes()

        elif choice == "3":
            run_full_audit()

        elif choice == "4":
            handle_snapshot()

        elif choice == "5":
            handle_baseline()

        elif choice == "6":
            handle_verify()

        elif choice == "7":
            handle_verify_evidence()

        elif choice == "8":
            handle_verify_report()

        elif choice == "9":
            handle_status()

        elif choice == "10":
            result = get_latest_report()

            if result is None:
                print_warning("No audit report found.")
            else:
                report = result["report"]
                summary = report.get("summary", {})

                print_header("LATEST AUDIT REPORT")

                print(f"Report     : {result['file']}")
                print(f"Generated  : {report.get('generated_at', 'N/A')}")
                print()

                print("SUMMARY")
                print_separator()

                print(f"Added      : {summary.get('added', 0)}")
                print(f"Removed    : {summary.get('removed', 0)}")
                print(f"Modified   : {summary.get('modified', 0)}")
                print(f"Unchanged  : {summary.get('unchanged', 0)}")

        elif choice == "11":
            print_success("Exiting SentinelTrace.")
            break

        print()
        input("Press Enter to return to the main menu...")


if __name__ == "__main__":
    main_menu()

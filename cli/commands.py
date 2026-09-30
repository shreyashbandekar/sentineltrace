from pathlib import Path

from audit.collector import collect_all
from audit.compare import compare_snapshots
from audit.integrity import calculate_hash
from audit.investigation import investigate_changes
from audit.report import format_report


PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASELINE_DIR = PROJECT_ROOT / "baseline"
SNAPSHOTS_DIR = PROJECT_ROOT / "snapshots"
REPORTS_DIR = PROJECT_ROOT / "reports"

BASELINE_FILE = BASELINE_DIR / "baseline.json"
BASELINE_HASH_FILE = BASELINE_DIR / "baseline.sha256"


def ensure_directories():
    """Create required project directories."""

    BASELINE_DIR.mkdir(exist_ok=True)
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)


def create_baseline():
    """Create the official pre-service baseline."""

    if BASELINE_FILE.exists():
        return {
            "success": False,
            "message": "Baseline already exists.",
        }

    snapshot = collect_all()

    BASELINE_DIR.mkdir(exist_ok=True)

    with BASELINE_FILE.open("w", encoding="utf-8") as file:
        import json

        json.dump(
            snapshot,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )

    baseline_hash = calculate_hash(snapshot)

    BASELINE_HASH_FILE.write_text(
        baseline_hash,
        encoding="utf-8",
    )

    return {
        "success": True,
        "baseline_file": str(BASELINE_FILE),
        "sha256": baseline_hash,
    }


def create_snapshot(timestamp_value):
    """Collect and save a new system snapshot."""

    import json

    snapshot = collect_all()

    snapshot_file = (
        SNAPSHOTS_DIR
        / f"snapshot_{timestamp_value}.json"
    )

    SNAPSHOTS_DIR.mkdir(exist_ok=True)

    with snapshot_file.open("w", encoding="utf-8") as file:
        json.dump(
            snapshot,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )

    return snapshot, snapshot_file


def compare_with_baseline(snapshot, timestamp_value):
    """Compare a snapshot against the official baseline."""

    import json

    if not BASELINE_FILE.exists():
        return {
            "success": False,
            "message": "No baseline found.",
        }

    with BASELINE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        baseline = json.load(file)

    comparison = compare_snapshots(
        baseline,
        snapshot,
    )
    findings = investigate_changes(comparison)

    added = 0
    removed = 0
    modified = 0
    unchanged = 0

    for section in comparison.values():

        if not isinstance(section, dict):
            continue

        added += len(section.get("added", []))
        removed += len(section.get("removed", []))
        modified += len(section.get("modified", []))
        unchanged += len(section.get("unchanged", []))
    audit_id = f"AUDIT-{timestamp_value.replace('_', '-')}"

    system_info = snapshot.get("system_info", {})

    report = {
        "audit_id": audit_id,
        "generated_at": timestamp_value,
        "metadata": {
            "computer_name": system_info.get("computer_name"),
            "username": system_info.get("username"),
            "operating_system": system_info.get("operating_system"),
            "os_release": system_info.get("os_release"),
            "os_version": system_info.get("os_version"),
            "architecture": system_info.get("architecture"),
        },
        "summary": {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged,
        },
        "comparison": comparison,
        "investigation": {
            "finding_count": len(findings),
            "findings": findings,
        },
    }

    REPORTS_DIR.mkdir(exist_ok=True)

    report_file = (
        REPORTS_DIR
        / f"report_{timestamp_value}.json"
    )

    with report_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )

    # Generate a human-readable TXT report.
    text_report = format_report(report)

    text_report_file = (
        REPORTS_DIR
        / f"report_{timestamp_value}.txt"
    )

    text_report_file.write_text(
        text_report,
        encoding="utf-8",
    )

    return {
        "success": True,
        "summary": report["summary"],
        "comparison": comparison,
        "report_file": str(report_file),
        "text_report_file": str(text_report_file),
    }


def verify_baseline():
    """Verify baseline integrity using SHA-256."""

    import json

    if not BASELINE_FILE.exists():
        return {
            "success": False,
            "message": "Baseline does not exist.",
        }

    if not BASELINE_HASH_FILE.exists():
        return {
            "success": False,
            "message": "Baseline hash does not exist.",
        }

    with BASELINE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        baseline = json.load(file)

    expected_hash = (
        BASELINE_HASH_FILE
        .read_text(encoding="utf-8")
        .strip()
    )

    actual_hash = calculate_hash(baseline)

    return {
        "success": True,
        "valid": expected_hash == actual_hash,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
    }


def get_status():
    """Return current project status."""

    ensure_directories()

    return {
        "baseline_exists": BASELINE_FILE.exists(),
        "hash_exists": BASELINE_HASH_FILE.exists(),
        "snapshot_count": len(
            list(SNAPSHOTS_DIR.glob("*.json"))
        ),
        "report_count": len(
            list(REPORTS_DIR.glob("*.json"))
        ),
    }


def get_latest_report():
    """Return the most recently generated audit report."""

    import json

    reports = sorted(
        REPORTS_DIR.glob("report_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not reports:
        return None

    latest_report = reports[0]

    with latest_report.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    return {
        "file": str(latest_report),
        "report": report,
    }
import json
from pathlib import Path


SECTION_ORDER = [
    "services",
    "software",
    "registry_startup",
    "startup",
    "scheduled_tasks",
    "drivers",
    "accounts",
    "network",
    "security",
    "system_info",
    "other", 
]


SECTION_TITLES = {
    "services": "SERVICES",
    "software": "SOFTWARE",
    "registry_startup": "REGISTRY STARTUP",
    "startup": "STARTUP FOLDERS",
    "scheduled_tasks": "SCHEDULED TASKS",
    "drivers": "DRIVERS",
    "accounts": "ACCOUNTS",
    "network": "NETWORK",
    "security": "SECURITY",
    "system_info": "SYSTEM INFORMATION",
    "other": "OTHER",
}


CHANGE_TYPE_ORDER = [
    "MODIFIED",
    "ADDED",
    "REMOVED",
]


def load_report(report_path):
    """Load an audit report from JSON."""

    path = Path(report_path)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def format_value(value):
    """Convert a value into readable single-line text."""

    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    if value is None:
        return "None"

    return str(value)


def format_changed_fields(changed_fields):
    """Format field-level changes for human-readable output."""

    lines = []

    for change in changed_fields or []:
        field = change.get("field", "Unknown")
        before = format_value(change.get("before"))
        after = format_value(change.get("after"))

        lines.append(f"    {field}:")
        lines.append(f"      BEFORE: {before}")
        lines.append(f"      AFTER : {after}")

    return lines


def get_finding_identifier(finding):
    """Get the best available identifier for a finding."""

    identifier = finding.get("id")

    if identifier and identifier != "Unknown":
        return identifier

    details = finding.get("details", {})

    after = details.get("after")

    if isinstance(after, dict):
        for field in (
            "TaskName",
            "Name",
            "DisplayName",
            "Path",
        ):
            value = after.get(field)

            if value:
                return str(value)

    before = details.get("before")

    if isinstance(before, dict):
        for field in (
            "TaskName",
            "Name",
            "DisplayName",
            "Path",
        ):
            value = before.get(field)

            if value:
                return str(value)

    return "Unknown"


def format_finding(finding):
    """Format a single investigation finding."""

    section = finding.get("section", "Unknown")
    change_type = finding.get("change_type", "Unknown")
    identifier = get_finding_identifier(finding)
    details = finding.get("details", {})

    lines = []

    lines.append(
        f"[{change_type}] {section}: {identifier}"
    )

    changed_fields = details.get(
        "changed_fields",
        [],
    )

    if changed_fields:
        lines.extend(
            format_changed_fields(changed_fields)
        )

    if change_type == "ADDED":
        lines.append(
            "    New item detected."
        )

    elif change_type == "REMOVED":
        lines.append(
            "    Item no longer present."
        )

    return lines


def normalize_section(section):
    """Normalize section names for report grouping."""

    section = str(section).lower().strip()

    if section in SECTION_TITLES:
        return section

    return "other"


def group_findings(findings):
    """Group findings by section and change type."""

    grouped = {}

    for finding in findings:
        section = normalize_section(
            finding.get("section", "other")
        )

        change_type = str(
            finding.get("change_type", "UNKNOWN")
        ).upper()

        if section not in grouped:
            grouped[section] = {}

        if change_type not in grouped[section]:
            grouped[section][change_type] = []

        grouped[section][change_type].append(
            finding
        )

    return grouped


def format_report(report):
    """Convert an audit report into a human-readable report."""

    lines = []

    lines.append("=" * 70)
    lines.append("SENTINELTRACE AUDIT REPORT")
    lines.append("=" * 70)
    lines.append("")

    lines.append(
        f"Audit ID   : {report.get('audit_id', 'Unknown')}"
    )

    lines.append(
        f"Generated  : {report.get('generated_at', 'Unknown')}"
    )

    metadata = report.get("metadata", {})

    lines.append("")
    lines.append("ENDPOINT INFORMATION")
    lines.append("-" * 70)

    lines.append(
        f"Computer Name : {metadata.get('computer_name', 'Unknown')}"
    )

    lines.append(
        f"Username      : {metadata.get('username', 'Unknown')}"
    )

    lines.append(
        f"Operating Sys.: {metadata.get('operating_system', 'Unknown')}"
    )

    lines.append(
        f"OS Version    : {metadata.get('os_release', 'Unknown')} "
        f"({metadata.get('os_version', 'Unknown')})"
    )

    lines.append(
        f"Architecture  : {metadata.get('architecture', 'Unknown')}"
    )

    lines.append("")

    summary = report.get("summary", {})

    lines.append("COMPARISON SUMMARY")
    lines.append("-" * 70)

    lines.append(
        f"Added      : {summary.get('added', 0)}"
    )

    lines.append(
        f"Removed    : {summary.get('removed', 0)}"
    )

    lines.append(
        f"Modified   : {summary.get('modified', 0)}"
    )

    lines.append(
        f"Unchanged  : {summary.get('unchanged', 0)}"
    )

    lines.append("")

    investigation = report.get(
        "investigation",
        {},
    )

    findings = investigation.get(
        "findings",
        [],
    )

    lines.append("INVESTIGATION SUMMARY")
    lines.append("-" * 70)

    lines.append(
        f"Total findings : {len(findings)}"
    )

    lines.append("")

    lines.append("INVESTIGATION FINDINGS")
    lines.append("-" * 70)

    lines.append("")

    if not findings:
        lines.append(
            "No changes requiring investigation."
        )

    else:
        grouped = group_findings(findings)

        for section in SECTION_ORDER:

            if section not in grouped:
                continue

            lines.append(
                SECTION_TITLES[section]
            )

            lines.append(
                "-" * 70
            )

            section_findings = grouped[section]

            for change_type in CHANGE_TYPE_ORDER:

                if change_type not in section_findings:
                    continue

                lines.append(
                    change_type
                )

                lines.append(
                    "-" * 30
                )

                for finding in section_findings[
                    change_type
                ]:
                    lines.extend(
                        format_finding(finding)
                    )

                    lines.append("")

            lines.append("")

    lines.append("=" * 70)
    lines.append("END OF AUDIT REPORT")
    lines.append("=" * 70)

    return "\n".join(lines)


def generate_text_report(report_path):
    """Load a JSON report and return formatted text."""

    report = load_report(report_path)

    return format_report(report)


if __name__ == "__main__":
    reports_dir = Path("reports")

    reports = sorted(
        reports_dir.glob("report_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not reports:
        print("No audit reports found.")

    else:
        latest_report = reports[0]

        print(
            generate_text_report(latest_report)
        )
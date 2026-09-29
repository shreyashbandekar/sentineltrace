from datetime import datetime


# These fields change during normal Windows task execution
# and should not be treated as meaningful configuration changes.
VOLATILE_TASK_FIELDS = {
    "LastRunTime",
    "NextRunTime",
    "LastTaskResult",
}


def get_changed_fields(before, after, section_name=None):
    """Return meaningful fields whose values changed."""

    changed_fields = []

    all_fields = set(before) | set(after)

    for field in sorted(all_fields):

        # Ignore expected runtime-only scheduled-task changes.
        if (
            section_name == "scheduled_tasks"
            and field in VOLATILE_TASK_FIELDS
        ):
            continue

        before_value = before.get(field)
        after_value = after.get(field)

        if before_value != after_value:
            changed_fields.append(
                {
                    "field": field,
                    "before": before_value,
                    "after": after_value,
                }
            )

    return changed_fields


def investigate_changes(comparison):
    """Build structured investigation findings from detected changes."""

    findings = []

    for section_name, section in comparison.items():

        modified = section.get("modified", [])
        added = section.get("added", [])
        removed = section.get("removed", [])

        # Added items
        for item in added:
            after = item.get("after", item)

            findings.append(
                {
                    "timestamp": datetime.now()
                    .astimezone()
                    .isoformat(timespec="seconds"),
                    "section": section_name,
                    "change_type": "ADDED",
                    "id": item.get("id", "Unknown"),
                    "details": {
                        "after": after,
                    },
                }
            )

        # Removed items
        for item in removed:
            before = item.get("before", item)

            findings.append(
                {
                    "timestamp": datetime.now()
                    .astimezone()
                    .isoformat(timespec="seconds"),
                    "section": section_name,
                    "change_type": "REMOVED",
                    "id": item.get("id", "Unknown"),
                    "details": {
                        "before": before,
                    },
                }
            )

        # Modified items
        for item in modified:
            before = item.get("before", {})
            after = item.get("after", {})

            changed_fields = get_changed_fields(
                before,
                after,
                section_name,
            )

            # Only create a finding when a meaningful field changed.
            if not changed_fields:
                continue

            findings.append(
                {
                    "timestamp": datetime.now()
                    .astimezone()
                    .isoformat(timespec="seconds"),
                    "section": section_name,
                    "change_type": "MODIFIED",
                    "id": item.get("id", "Unknown"),
                    "details": {
                        "changed_fields": changed_fields,
                        "before": before,
                        "after": after,
                    },
                }
            )

    return findings


if __name__ == "__main__":
    print("Investigation module: OK")
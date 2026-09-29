import json
from pathlib import Path


BASELINE_FILE = (
    Path(__file__).resolve().parent.parent
    / "baseline"
    / "baseline.json"
)

# These fields change naturally when Windows executes a scheduled task.
# They should be tracked, but should not automatically count as a
# structural modification.
VOLATILE_TASK_FIELDS = {
    "LastRunTime",
    "NextRunTime",
    "LastTaskResult",
}


def load_json(file_path):
    """Load JSON data from a file."""

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def compare_values(baseline, current):
    """Compare two values."""

    if baseline == current:
        return {
            "status": "UNCHANGED",
            "before": baseline,
            "after": current,
        }

    return {
        "status": "MODIFIED",
        "before": baseline,
        "after": current,
    }


def compare_lists(baseline, current, key):
    """Compare two lists of objects using a unique identifying key."""

    baseline_map = {
        str(item.get(key)): item
        for item in baseline
        if isinstance(item, dict) and key in item
    }

    current_map = {
        str(item.get(key)): item
        for item in current
        if isinstance(item, dict) and key in item
    }

    added = []
    removed = []
    modified = []
    unchanged = []

    for item_id, current_item in current_map.items():

        if item_id not in baseline_map:
            added.append(current_item)

        elif baseline_map[item_id] != current_item:
            modified.append(
                {
                    "id": item_id,
                    "before": baseline_map[item_id],
                    "after": current_item,
                }
            )

        else:
            unchanged.append(current_item)

    for item_id, baseline_item in baseline_map.items():

        if item_id not in current_map:
            removed.append(baseline_item)

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }


def normalize_scheduled_task(task):
    """
    Remove naturally changing execution metadata before comparing
    scheduled-task structure.
    """

    if not isinstance(task, dict):
        return task

    normalized = dict(task)

    for field in VOLATILE_TASK_FIELDS:
        normalized.pop(field, None)

    return normalized


def compare_scheduled_tasks(baseline, current):
    """
    Compare scheduled tasks while separating:
    - structural changes
    - normal runtime changes
    - additions
    - removals
    - unchanged tasks
    """

    baseline_map = {
        str(item.get("TaskPath", "") + item.get("TaskName", "")): item
        for item in baseline
        if isinstance(item, dict)
    }

    current_map = {
        str(item.get("TaskPath", "") + item.get("TaskName", "")): item
        for item in current
        if isinstance(item, dict)
    }

    added = []
    removed = []
    modified = []
    runtime_changed = []
    unchanged = []

    for task_id, current_task in current_map.items():

        if task_id not in baseline_map:
            added.append(current_task)
            continue

        baseline_task = baseline_map[task_id]

        # Completely unchanged.
        if baseline_task == current_task:
            unchanged.append(current_task)
            continue

        normalized_baseline = normalize_scheduled_task(
            baseline_task
        )

        normalized_current = normalize_scheduled_task(
            current_task
        )

        # Only volatile execution information changed.
        if normalized_baseline == normalized_current:

            changed_runtime_fields = []

            for field in VOLATILE_TASK_FIELDS:
                before = baseline_task.get(field)
                after = current_task.get(field)

                if before != after:
                    changed_runtime_fields.append(
                        {
                            "field": field,
                            "before": before,
                            "after": after,
                        }
                    )

            runtime_changed.append(
                {
                    "id": task_id,
                    "runtime_changes": changed_runtime_fields,
                }
            )

        else:
            # Something structural changed.
            modified.append(
                {
                    "id": task_id,
                    "before": baseline_task,
                    "after": current_task,
                }
            )

    for task_id, baseline_task in baseline_map.items():

        if task_id not in current_map:
            removed.append(baseline_task)

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "runtime_changed": runtime_changed,
        "unchanged": unchanged,
    }


def compare_snapshots(baseline, current):
    """Compare a current snapshot against the official baseline."""

    results = {}

    results["users"] = compare_lists(
        baseline["accounts"]["users"],
        current["accounts"]["users"],
        "Name",
    )

    results["administrators"] = compare_lists(
        baseline["accounts"]["administrators"],
        current["accounts"]["administrators"],
        "Name",
    )

    results["services"] = compare_lists(
        baseline["services"],
        current["services"],
        "Name",
    )

    results["software"] = compare_lists(
        baseline["software"],
        current["software"],
        "DisplayName",
    )

    results["network_adapters"] = compare_lists(
        baseline["network"]["adapters"],
        current["network"]["adapters"],
        "Name",
    )

    results["security"] = compare_values(
        baseline["security"],
        current["security"],
    )

    results["registry_startup"] = compare_lists(
        baseline["startup"]["registry_startup"],
        current["startup"]["registry_startup"],
        "Name",
    )

    results["startup_folders"] = compare_lists(
        baseline["startup"]["startup_folders"],
        current["startup"]["startup_folders"],
        "FullName",
    )

    results["scheduled_tasks"] = compare_scheduled_tasks(
        baseline["scheduled_tasks"]["tasks"],
        current["scheduled_tasks"]["tasks"],
    )

    results["drivers"] = compare_lists(
        baseline["drivers"]["drivers"],
        current["drivers"]["drivers"],
        "Name",
    )

    return results


if __name__ == "__main__":

    baseline = load_json(BASELINE_FILE)

    print("========================================")
    print("       COMPARISON ENGINE TEST")
    print("========================================")
    print()

    print(f"Baseline loaded: {BASELINE_FILE}")
    print()

    print("Comparison engine is ready.")
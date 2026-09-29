from audit.investigation import investigate_changes


def test_detects_modified_service():
    comparison = {
        "services": {
            "added": [],
            "removed": [],
            "modified": [
                {
                    "before": {
                        "Name": "TestService",
                        "State": "Stopped",
                    },
                    "after": {
                        "Name": "TestService",
                        "State": "Running",
                    },
                }
            ],
            "unchanged": [],
        }
    }

    findings = investigate_changes(comparison)

    assert len(findings) == 1
    assert findings[0]["section"] == "services"
    assert findings[0]["change_type"] == "MODIFIED"
    assert findings[0]["details"]["changed_fields"][0]["field"] == "State"
    assert findings[0]["details"]["changed_fields"][0]["before"] == "Stopped"
    assert findings[0]["details"]["changed_fields"][0]["after"] == "Running"


def test_detects_added_service():
    comparison = {
        "services": {
            "added": [
                {
                    "Name": "NewService",
                    "State": "Running",
                }
            ],
            "removed": [],
            "modified": [],
            "unchanged": [],
        }
    }

    findings = investigate_changes(comparison)

    assert len(findings) == 1
    assert findings[0]["section"] == "services"
    assert findings[0]["change_type"] == "ADDED"
    assert findings[0]["details"]["after"]["Name"] == "NewService"


def test_detects_removed_service():
    comparison = {
        "services": {
            "added": [],
            "removed": [
                {
                    "Name": "OldService",
                    "State": "Running",
                }
            ],
            "modified": [],
            "unchanged": [],
        }
    }

    findings = investigate_changes(comparison)

    assert len(findings) == 1
    assert findings[0]["section"] == "services"
    assert findings[0]["change_type"] == "REMOVED"
    assert findings[0]["details"]["before"]["Name"] == "OldService"

def test_ignores_volatile_scheduled_task_fields():
    comparison = {
        "scheduled_tasks": {
            "added": [],
            "removed": [],
            "modified": [
                {
                    "before": {
                        "TaskName": "TestTask",
                        "State": "Ready",
                        "LastRunTime": "2026-09-25T10:00:00",
                        "NextRunTime": "2026-09-25T11:00:00",
                        "LastTaskResult": 0,
                    },
                    "after": {
                        "TaskName": "TestTask",
                        "State": "Ready",
                        "LastRunTime": "2026-09-25T10:30:00",
                        "NextRunTime": "2026-09-25T11:30:00",
                        "LastTaskResult": 0,
                    },
                }
            ],
            "unchanged": [],
        }
    }

    findings = investigate_changes(comparison)

    assert len(findings) == 0


def test_detects_real_scheduled_task_change():
    comparison = {
        "scheduled_tasks": {
            "added": [],
            "removed": [],
            "modified": [
                {
                    "before": {
                        "TaskName": "TestTask",
                        "State": "Ready",
                        "RunLevel": "Limited",
                        "LastRunTime": "2026-09-25T10:00:00",
                        "NextRunTime": "2026-09-25T11:00:00",
                        "LastTaskResult": 0,
                    },
                    "after": {
                        "TaskName": "TestTask",
                        "State": "Ready",
                        "RunLevel": "Highest",
                        "LastRunTime": "2026-09-25T10:30:00",
                        "NextRunTime": "2026-09-25T11:30:00",
                        "LastTaskResult": 0,
                    },
                }
            ],
            "unchanged": [],
        }
    }

    findings = investigate_changes(comparison)

    assert len(findings) == 1
    assert findings[0]["section"] == "scheduled_tasks"
    assert findings[0]["change_type"] == "MODIFIED"

    changed_fields = findings[0]["details"]["changed_fields"]

    assert len(changed_fields) == 1
    assert changed_fields[0]["field"] == "RunLevel"
    assert changed_fields[0]["before"] == "Limited"
    assert changed_fields[0]["after"] == "Highest"
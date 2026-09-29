from audit.compare import compare_snapshots


def make_snapshot(services):
    """Create a minimal valid snapshot for comparison tests."""

    return {
        "accounts": {
            "users": [],
            "administrators": [],
        },
        "services": services,
        "software": [],
        "network": {
            "adapters": [],
            "ip_configuration": [],
            "tcp_connections": [],
        },
        "security": {
            "windows_defender": [],
            "firewall_profiles": [],
            "uac": [],
            "remote_desktop": [],
            "winrm": [],
            "remote_assistance": [],
        },
        "startup": {
            "registry_startup": [],
            "startup_folders": [],
            "boot_logon_scheduled_tasks": [],
        },
        "scheduled_tasks": {
            "tasks": [],
        },
        "drivers": {
            "drivers": [],
        },
    }


def test_detects_added_service():
    before = make_snapshot([
        {
            "Name": "WindowsService",
            "State": "Running",
        }
    ])

    after = make_snapshot([
        {
            "Name": "WindowsService",
            "State": "Running",
        },
        {
            "Name": "NewService",
            "State": "Running",
        },
    ])

    result = compare_snapshots(before, after)

    assert len(result["services"]["added"]) == 1
    assert result["services"]["added"][0]["Name"] == "NewService"


def test_detects_removed_service():
    before = make_snapshot([
        {
            "Name": "OldService",
            "State": "Running",
        }
    ])

    after = make_snapshot([])

    result = compare_snapshots(before, after)

    assert len(result["services"]["removed"]) == 1
    assert result["services"]["removed"][0]["Name"] == "OldService"


def test_detects_modified_service():
    before = make_snapshot([
        {
            "Name": "WindowsService",
            "State": "Stopped",
        }
    ])

    after = make_snapshot([
        {
            "Name": "WindowsService",
            "State": "Running",
        }
    ])

    result = compare_snapshots(before, after)

    assert len(result["services"]["modified"]) == 1

    modified = result["services"]["modified"][0]

    assert modified["id"] == "WindowsService"
    assert modified["before"]["State"] == "Stopped"
    assert modified["after"]["State"] == "Running"


def test_detects_unchanged_service():
    before = make_snapshot([
        {
            "Name": "WindowsService",
            "State": "Running",
        }
    ])

    after = make_snapshot([
        {
            "Name": "WindowsService",
            "State": "Running",
        }
    ])

    result = compare_snapshots(before, after)

    assert len(result["services"]["added"]) == 0
    assert len(result["services"]["removed"]) == 0
    assert len(result["services"]["modified"]) == 0
    assert len(result["services"]["unchanged"]) == 1
from pathlib import Path

from cli.commands import (
    compare_with_baseline,
    create_baseline,
    create_snapshot,
    get_status,
    verify_baseline,
)


def test_get_status():
    result = get_status()

    assert result["baseline_exists"] is True
    assert result["hash_exists"] is True
    assert result["snapshot_count"] >= 1
    assert result["report_count"] >= 1



def test_create_snapshot(tmp_path, monkeypatch):
    import cli.commands as commands

    monkeypatch.setattr(
        commands,
        "SNAPSHOTS_DIR",
        tmp_path,
    )

    timestamp = "20990101_120000"

    snapshot, snapshot_file = create_snapshot(timestamp)

    assert snapshot_file.exists()
    assert snapshot_file.name == "snapshot_20990101_120000.json"

    assert isinstance(snapshot, dict)
    assert "system_info" in snapshot
    assert "accounts" in snapshot
    assert "services" in snapshot
    assert "software" in snapshot
    assert "network" in snapshot
    assert "security" in snapshot
    assert "startup" in snapshot
    assert "scheduled_tasks" in snapshot
    assert "drivers" in snapshot


def test_create_baseline_refuses_overwrite():
    result = create_baseline()

    assert result["success"] is False
    assert result["message"] == "Baseline already exists."

def test_compare_with_baseline(tmp_path, monkeypatch):
    import json
    import cli.commands as commands

    baseline_file = tmp_path / "baseline.json"
    reports_dir = tmp_path / "reports"

    baseline = {
        "accounts": {
            "users": [],
            "administrators": [],
        },
        "services": [
            {
                "Name": "TestService",
                "State": "Stopped",
            }
        ],
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

    current = {
        "accounts": {
            "users": [],
            "administrators": [],
        },
        "services": [
            {
                "Name": "TestService",
                "State": "Running",
            }
        ],
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

    baseline_file.write_text(
        json.dumps(baseline),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        commands,
        "BASELINE_FILE",
        baseline_file,
    )

    monkeypatch.setattr(
        commands,
        "REPORTS_DIR",
        reports_dir,
    )

    result = compare_with_baseline(
        current,
        "20990101_120000",
    )

    assert result["success"] is True
    assert result["summary"]["modified"] == 1

    assert result["report_file"] is not None
    assert result["text_report_file"] is not None

    assert reports_dir.exists()

    assert Path(result["report_file"]).exists()
    assert Path(result["text_report_file"]).exists()


def test_compare_without_baseline(tmp_path, monkeypatch):
    import cli.commands as commands

    missing_baseline = tmp_path / "missing_baseline.json"

    monkeypatch.setattr(
        commands,
        "BASELINE_FILE",
        missing_baseline,
    )

    result = compare_with_baseline(
        {},
        "20990101_120000",
    )

    assert result["success"] is False
    assert result["message"] == "No baseline found."


def test_verify_baseline_detects_tampering(
    tmp_path,
    monkeypatch,
):
    import json
    import cli.commands as commands
    from audit.integrity import calculate_hash

    baseline_file = tmp_path / "baseline.json"
    hash_file = tmp_path / "baseline.sha256"

    original_data = {
        "system_info": {
            "computer_name": "TEST-PC",
        }
    }

    baseline_file.write_text(
        json.dumps(original_data),
        encoding="utf-8",
    )

    original_hash = calculate_hash(original_data)

    hash_file.write_text(
        original_hash,
        encoding="utf-8",
    )

    # Simulate tampering after the baseline was created.
    tampered_data = {
        "system_info": {
            "computer_name": "MODIFIED-PC",
        }
    }

    baseline_file.write_text(
        json.dumps(tampered_data),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        commands,
        "BASELINE_FILE",
        baseline_file,
    )

    monkeypatch.setattr(
        commands,
        "BASELINE_HASH_FILE",
        hash_file,
    )

    result = commands.verify_baseline()

    assert result["success"] is True
    assert result["valid"] is False
    assert result["expected_hash"] != result["actual_hash"]

def test_verify_baseline_missing_hash(
    tmp_path,
    monkeypatch,
):
    import json
    import cli.commands as commands

    baseline_file = tmp_path / "baseline.json"
    hash_file = tmp_path / "missing.sha256"

    baseline_file.write_text(
        json.dumps({
            "system_info": {
                "computer_name": "TEST-PC",
            }
        }),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        commands,
        "BASELINE_FILE",
        baseline_file,
    )

    monkeypatch.setattr(
        commands,
        "BASELINE_HASH_FILE",
        hash_file,
    )

    result = commands.verify_baseline()

    assert result["success"] is False
    assert result["message"] == "Baseline hash does not exist."
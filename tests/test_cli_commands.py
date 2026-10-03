from pathlib import Path

from cli.commands import (
    compare_with_baseline,
    create_baseline,
    create_snapshot,
    get_status,
    verify_baseline,
)


def test_get_status(tmp_path, monkeypatch):
    import cli.commands as commands

    baseline_dir = tmp_path / "baseline"
    snapshots_dir = tmp_path / "snapshots"
    reports_dir = tmp_path / "reports"

    baseline_dir.mkdir()
    snapshots_dir.mkdir()
    reports_dir.mkdir()

    baseline_file = baseline_dir / "baseline.json"
    hash_file = baseline_dir / "baseline.sha256"

    baseline_file.write_text("{}", encoding="utf-8")
    hash_file.write_text("test-hash", encoding="utf-8")

    (snapshots_dir / "snapshot_test.json").write_text(
        "{}",
        encoding="utf-8",
    )

    (reports_dir / "report_test.json").write_text(
        "{}",
        encoding="utf-8",
    )

    monkeypatch.setattr(commands, "BASELINE_FILE", baseline_file)
    monkeypatch.setattr(commands, "BASELINE_HASH_FILE", hash_file)
    monkeypatch.setattr(commands, "SNAPSHOTS_DIR", snapshots_dir)
    monkeypatch.setattr(commands, "REPORTS_DIR", reports_dir)

    result = get_status()

    assert result["baseline_exists"] is True
    assert result["hash_exists"] is True
    assert result["snapshot_count"] == 1
    assert result["report_count"] == 1



def test_create_snapshot(tmp_path, monkeypatch):
    import cli.commands as commands

    monkeypatch.setattr(
        commands,
        "SNAPSHOTS_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        commands,
        "collect_all",
        lambda: {
            "system_info": {},
            "accounts": {
                "users": [],
                "administrators": [],
            },
            "services": [],
            "software": [],
            "network": {
                "adapters": [],
                "ip_configuration": [],
                "tcp_connections": [],
            },
            "security": {},
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
        },
    )

    timestamp = "20990101_120000"

    snapshot, snapshot_file,  snapshot_hash = create_snapshot(timestamp)
    snapshot_hash_file = Path(
        f"{snapshot_file}.sha256"
    )

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




def test_create_baseline_refuses_overwrite(tmp_path, monkeypatch):
    import cli.commands as commands

    baseline_file = tmp_path / "baseline.json"

    baseline_file.write_text(
        "{}",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        commands,
        "BASELINE_FILE",
        baseline_file,
    )

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
        "system_info": {
            "computer_name": "TEST-PC",
            "username": "test-user",
            "operating_system": "Windows",
            "os_release": "11",
            "os_version": "10.0.26200",
            "architecture": "AMD64",
        },
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
    report_hash_file = Path(result["report_hash_file"])
    text_report_hash_file = Path(result["text_report_hash_file"])

    assert report_hash_file.exists()
    assert text_report_hash_file.exists()

    assert len(result["report_hash"]) == 64
    assert len(result["text_report_hash"]) == 64

    assert (
        report_hash_file.read_text(encoding="utf-8").strip()
        == result["report_hash"]
    )

    assert (
        text_report_hash_file.read_text(encoding="utf-8").strip()
        == result["text_report_hash"]
    )


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

def test_verify_evidence(tmp_path, monkeypatch):
    from cli.commands import verify_evidence

    evidence_file = tmp_path / "evidence.json"
    evidence_file.write_text('{"test": "data"}', encoding="utf-8")

    hash_file = Path(f"{evidence_file}.sha256")

    from audit.integrity import write_file_hash

    expected_hash = write_file_hash(evidence_file, hash_file)

    result = verify_evidence(evidence_file)

    assert result["success"] is True
    assert result["file"] == str(evidence_file)
    assert result["expected_hash"] == expected_hash
    assert result["actual_hash"] == expected_hash
    assert result["hash_file"] == str(hash_file)

def test_verify_evidence_detects_tampering(tmp_path):
    from cli.commands import verify_evidence
    from audit.integrity import write_file_hash

    evidence_file = tmp_path / "evidence.json"
    evidence_file.write_text(
        '{"status": "original"}',
        encoding="utf-8",
    )

    hash_file = Path(f"{evidence_file}.sha256")
    write_file_hash(evidence_file, hash_file)

    # Tamper with the evidence after its hash was created.
    evidence_file.write_text(
        '{"status": "tampered"}',
        encoding="utf-8",
    )

    result = verify_evidence(evidence_file)

    assert result["success"] is False
    assert result["expected_hash"] != result["actual_hash"]

def test_get_evidence_files(tmp_path, monkeypatch):
    from cli.commands import get_evidence_files

    monkeypatch.setattr(
        "cli.commands.SNAPSHOTS_DIR",
        tmp_path,
    )

    snapshot_1 = tmp_path / "snapshot_20261001_120000.json"
    snapshot_2 = tmp_path / "snapshot_20261002_120000.json"
    ignored_file = tmp_path / "notes.txt"

    snapshot_1.write_text("{}", encoding="utf-8")
    snapshot_2.write_text("{}", encoding="utf-8")
    ignored_file.write_text("ignore", encoding="utf-8")

    result = get_evidence_files()

    assert result == [
        snapshot_1,
        snapshot_2,
    ]

def test_get_verifiable_evidence_files(tmp_path, monkeypatch):
    from cli.commands import get_verifiable_evidence_files

    monkeypatch.setattr(
        "cli.commands.SNAPSHOTS_DIR",
        tmp_path,
    )

    verified_snapshot = tmp_path / "snapshot_20261002_120000.json"
    unverified_snapshot = tmp_path / "snapshot_20261001_120000.json"

    verified_snapshot.write_text("{}", encoding="utf-8")
    unverified_snapshot.write_text("{}", encoding="utf-8")

    verified_hash = Path(f"{verified_snapshot}.sha256")
    verified_hash.write_text(
        "a" * 64,
        encoding="utf-8",
    )

    result = get_verifiable_evidence_files()

    assert result == [verified_snapshot]

def test_get_verifiable_report_files(tmp_path, monkeypatch):
    from cli.commands import get_verifiable_report_files

    monkeypatch.setattr(
        "cli.commands.REPORTS_DIR",
        tmp_path,
    )

    verified_report = tmp_path / "report_20261002_120000.json"
    unverified_report = tmp_path / "report_20261001_120000.json"

    verified_report.write_text("{}", encoding="utf-8")
    unverified_report.write_text("{}", encoding="utf-8")

    verified_hash = Path(f"{verified_report}.sha256")
    verified_hash.write_text(
        "a" * 64,
        encoding="utf-8",
    )

    result = get_verifiable_report_files()

    assert result == [verified_report]

def test_verify_report(tmp_path):
    from cli.commands import verify_report
    from audit.integrity import write_file_hash

    report_file = tmp_path / "report_20261002_120000.json"

    report_file.write_text(
        '{"status": "complete"}',
        encoding="utf-8",
    )

    hash_file = Path(f"{report_file}.sha256")
    expected_hash = write_file_hash(
        report_file,
        hash_file,
    )

    result = verify_report(report_file)

    assert result["success"] is True
    assert result["file"] == str(report_file)
    assert result["expected_hash"] == expected_hash
    assert result["actual_hash"] == expected_hash
    assert result["hash_file"] == str(hash_file)

def test_verify_report_detects_tampering(tmp_path):
    import cli.commands as commands
    from audit.integrity import write_file_hash
    report_file = tmp_path / "report_test.json"
    hash_file = tmp_path / "report_test.json.sha256"

    report_file.write_text(
        '{"status": "original"}',
        encoding="utf-8",
    )

    write_file_hash(report_file, hash_file)

    report_file.write_text(
        '{"status": "tampered"}',
        encoding="utf-8",
    )

    result = commands.verify_report(report_file)

    assert result["success"] is False
    assert result["actual_hash"] != result["expected_hash"]
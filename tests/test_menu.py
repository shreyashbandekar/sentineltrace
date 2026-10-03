from pathlib import Path

from cli import menu


def test_handle_verify_evidence_verified(monkeypatch, capsys):
    evidence_file = Path("snapshots/snapshot_20261002_003853.json")

    monkeypatch.setattr(
        menu,
        "get_verifiable_evidence_files",
        lambda: [evidence_file],
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "1",
    )

    monkeypatch.setattr(
        menu,
        "verify_evidence",
        lambda _: {
            "success": True,
            "file": str(evidence_file),
            "hash_file": f"{evidence_file}.sha256",
            "expected_hash": "a" * 64,
            "actual_hash": "a" * 64,
        },
    )

    menu.handle_verify_evidence()

    output = capsys.readouterr().out

    assert "EVIDENCE INTEGRITY" in output
    assert "Evidence integrity verified." in output


def test_handle_verify_evidence_no_files(monkeypatch, capsys):
    monkeypatch.setattr(
        menu,
        "get_verifiable_evidence_files",
        lambda: [],
    )

    menu.handle_verify_evidence()

    output = capsys.readouterr().out

    assert "No evidence files found." in output

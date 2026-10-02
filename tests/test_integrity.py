from pathlib import Path

from audit.integrity import (
    calculate_hash,
    calculate_file_hash,
    verify_file_hash,
)


def test_calculate_hash_is_deterministic():
    data = {
        "name": "SentinelTrace",
        "version": 1,
    }

    first_hash = calculate_hash(data)
    second_hash = calculate_hash(data)

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_calculate_hash_is_order_independent():
    first = {
        "name": "SentinelTrace",
        "version": 1,
    }

    second = {
        "version": 1,
        "name": "SentinelTrace",
    }

    assert calculate_hash(first) == calculate_hash(second)


def test_calculate_file_hash(tmp_path):
    test_file = Path(tmp_path) / "test.txt"
    test_file.write_text("SentinelTrace integrity test", encoding="utf-8")

    file_hash = calculate_file_hash(test_file)

    assert len(file_hash) == 64


def test_verify_file_hash(tmp_path):
    test_file = Path(tmp_path) / "test.txt"
    test_file.write_text("SentinelTrace integrity test", encoding="utf-8")

    expected_hash = calculate_file_hash(test_file)

    assert verify_file_hash(test_file, expected_hash) is True


def test_verify_file_hash_detects_tampering(tmp_path):
    test_file = Path(tmp_path) / "test.txt"
    test_file.write_text("Original content", encoding="utf-8")

    expected_hash = calculate_file_hash(test_file)

    test_file.write_text("Modified content", encoding="utf-8")

    assert verify_file_hash(test_file, expected_hash) is False

def test_write_file_hash(tmp_path):
    test_file = Path(tmp_path) / "test.txt"
    hash_file = Path(tmp_path) / "test.txt.sha256"

    test_file.write_text(
        "SentinelTrace integrity test",
        encoding="utf-8",
    )

    from audit.integrity import write_file_hash

    returned_hash = write_file_hash(
        test_file,
        hash_file,
    )

    assert hash_file.exists()
    assert len(returned_hash) == 64
    assert hash_file.read_text(encoding="utf-8") == returned_hash
    assert verify_file_hash(test_file, returned_hash) is True
import hashlib
import json
from pathlib import Path


def canonical_json(data):
    """Convert data into deterministic JSON for hashing."""
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def calculate_hash(data):
    """Calculate SHA-256 hash of a Python object."""
    canonical_data = canonical_json(data)

    return hashlib.sha256(
        canonical_data.encode("utf-8")
    ).hexdigest()


def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    path = Path(file_path)

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_file_hash(file_path, expected_hash):
    """Verify a file against an expected SHA-256 hash."""
    actual_hash = calculate_file_hash(file_path)

    return actual_hash.lower() == expected_hash.strip().lower()


if __name__ == "__main__":
    print("Integrity module: OK")
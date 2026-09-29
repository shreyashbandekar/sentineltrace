import hashlib
import json
from pathlib import Path

from collector import collect_all


BASELINE_DIR = Path(__file__).resolve().parent.parent / "baseline"
BASELINE_FILE = BASELINE_DIR / "baseline.json"
HASH_FILE = BASELINE_DIR / "baseline.sha256"


def canonical_json(data):
    """Convert data to deterministic JSON for hashing."""
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def calculate_hash(data):
    """Calculate SHA-256 hash of the snapshot."""
    canonical_data = canonical_json(data)

    return hashlib.sha256(
        canonical_data.encode("utf-8")
    ).hexdigest()


def create_baseline():
    """Collect and save the current system state as the baseline."""

    snapshot = collect_all()

    baseline_hash = calculate_hash(snapshot)

    BASELINE_DIR.mkdir(parents=True, exist_ok=True)

    with BASELINE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            snapshot,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )

    HASH_FILE.write_text(
        baseline_hash,
        encoding="utf-8",
    )

    return {
        "baseline_file": str(BASELINE_FILE),
        "hash_file": str(HASH_FILE),
        "sha256": baseline_hash,
    }


if __name__ == "__main__":
    result = create_baseline()

    print()
    print("========================================")
    print("       BASELINE CREATED SUCCESSFULLY")
    print("========================================")
    print()
    print(f"Baseline : {result['baseline_file']}")
    print(f"SHA-256  : {result['sha256']}")
    print(f"Hash file: {result['hash_file']}")
    print()
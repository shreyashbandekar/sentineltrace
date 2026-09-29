from audit.integrity import calculate_hash


def test_baseline_hash_matches_data():
    data = {
        "system_info": {
            "computer_name": "TEST-PC",
            "username": "testuser",
        },
        "security": {
            "firewall": True,
        },
    }

    expected_hash = calculate_hash(data)
    actual_hash = calculate_hash(data)

    assert expected_hash == actual_hash


def test_modified_baseline_changes_hash():
    original_data = {
        "system_info": {
            "computer_name": "TEST-PC",
            "username": "testuser",
        }
    }

    modified_data = {
        "system_info": {
            "computer_name": "TEST-PC",
            "username": "attacker",
        }
    }

    original_hash = calculate_hash(original_data)
    modified_hash = calculate_hash(modified_data)

    assert original_hash != modified_hash


def test_baseline_hash_detects_added_data():
    original_data = {
        "users": [
            "shrey",
        ]
    }

    modified_data = {
        "users": [
            "shrey",
            "new_user",
        ]
    }

    original_hash = calculate_hash(original_data)
    modified_hash = calculate_hash(modified_data)

    assert original_hash != modified_hash
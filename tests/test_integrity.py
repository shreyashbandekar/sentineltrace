from audit.integrity import calculate_hash


def test_same_data_produces_same_hash():
    data = {
        "username": "shrey",
        "status": "active",
    }

    hash_one = calculate_hash(data)
    hash_two = calculate_hash(data)

    assert hash_one == hash_two


def test_different_data_produces_different_hash():
    data_one = {
        "username": "shrey",
        "status": "active",
    }

    data_two = {
        "username": "shrey",
        "status": "disabled",
    }

    hash_one = calculate_hash(data_one)
    hash_two = calculate_hash(data_two)

    assert hash_one != hash_two


def test_hash_is_sha256_format():
    data = {
        "test": "value",
    }

    result = calculate_hash(data)

    assert len(result) == 64
    assert all(
        character in "0123456789abcdef"
        for character in result
    )
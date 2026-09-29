from audit.accounts import collect_accounts


def test_collect_accounts():
    result = collect_accounts()

    assert isinstance(result, dict)

    assert "users" in result
    assert "administrators" in result

    assert isinstance(result["users"], list)
    assert isinstance(result["administrators"], list)

    for user in result["users"]:
        assert "Name" in user
        assert "Enabled" in user

    for administrator in result["administrators"]:
        assert "Name" in administrator
        assert "ObjectClass" in administrator
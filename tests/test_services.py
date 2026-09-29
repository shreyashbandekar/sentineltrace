from audit.services import collect_services


def test_collect_services():
    result = collect_services()

    assert isinstance(result, list)

    for service in result:
        assert "Name" in service
        assert "DisplayName" in service
        assert "State" in service
        assert "StartMode" in service
        assert "StartName" in service
        assert "PathName" in service
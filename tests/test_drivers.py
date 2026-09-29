from audit.drivers import collect_drivers


def test_collect_drivers():
    result = collect_drivers()

    assert isinstance(result, dict)

    assert "driver_count" in result
    assert "drivers" in result

    assert isinstance(result["driver_count"], int)
    assert isinstance(result["drivers"], list)

    assert result["driver_count"] == len(result["drivers"])

    for driver in result["drivers"]:
        assert "Name" in driver
        assert "DisplayName" in driver
        assert "State" in driver
        assert "StartMode" in driver
        assert "StartName" in driver
        assert "PathName" in driver
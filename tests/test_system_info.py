from audit.system_info import collect_system_info


def test_collect_system_info():
    result = collect_system_info()

    assert isinstance(result, dict)

    assert "timestamp" in result
    assert "computer_name" in result
    assert "username" in result
    assert "operating_system" in result
    assert "os_release" in result
    assert "os_version" in result
    assert "architecture" in result
    assert "python_version" in result

    assert result["operating_system"] == "Windows"
    assert result["computer_name"]
    assert result["username"]
    assert result["python_version"]
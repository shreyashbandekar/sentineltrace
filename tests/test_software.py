from audit.software import collect_software


def test_collect_software():
    result = collect_software()

    assert isinstance(result, list)

    for software in result:
        assert "DisplayName" in software
        assert "DisplayVersion" in software
        assert "Publisher" in software
        assert "InstallDate" in software
        assert "InstallLocation" in software
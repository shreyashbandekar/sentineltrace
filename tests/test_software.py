import json

import audit.software as software


def test_collect_software(monkeypatch):
    expected_software = [
        {
            "DisplayName": "Test Application",
            "DisplayVersion": "1.0.0",
            "Publisher": "Test Publisher",
            "InstallDate": "20260930",
            "InstallLocation": "C:\\Program Files\\Test Application",
        }
    ]

    class FakeResult:
        returncode = 0
        stdout = json.dumps(expected_software)
        stderr = ""

    monkeypatch.setattr(
        software.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    result = software.collect_software()

    assert isinstance(result, list)
    assert result == expected_software

    for item in result:
        assert "DisplayName" in item
        assert "DisplayVersion" in item
        assert "Publisher" in item
        assert "InstallDate" in item
        assert "InstallLocation" in item
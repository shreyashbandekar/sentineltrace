import audit.collector as collector


def test_collect_all(monkeypatch):
    monkeypatch.setattr(
        collector,
        "collect_system_info",
        lambda: {"hostname": "TEST-HOST"},
    )

    monkeypatch.setattr(
        collector,
        "collect_accounts",
        lambda: {
            "users": [],
            "administrators": [],
        },
    )

    monkeypatch.setattr(
        collector,
        "collect_services",
        lambda: [],
    )

    monkeypatch.setattr(
        collector,
        "collect_software",
        lambda: [],
    )

    monkeypatch.setattr(
        collector,
        "collect_network",
        lambda: {
            "adapters": [],
            "ip_configuration": [],
            "tcp_connections": [],
        },
    )

    monkeypatch.setattr(
        collector,
        "collect_security",
        lambda: {},
    )

    monkeypatch.setattr(
        collector,
        "collect_startup",
        lambda: {
            "registry_startup": [],
            "startup_folders": [],
            "boot_logon_scheduled_tasks": [],
        },
    )

    monkeypatch.setattr(
        collector,
        "collect_tasks",
        lambda: {
            "tasks": [],
        },
    )

    monkeypatch.setattr(
        collector,
        "collect_drivers",
        lambda: {
            "driver_count": 0,
            "drivers": [],
        },
    )

    result = collector.collect_all()

    assert isinstance(result, dict)

    expected_sections = {
        "system_info",
        "accounts",
        "services",
        "software",
        "network",
        "security",
        "startup",
        "scheduled_tasks",
        "drivers",
    }

    assert set(result.keys()) == expected_sections

    for section in expected_sections:
        assert result[section] is not None
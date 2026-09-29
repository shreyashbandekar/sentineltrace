from audit.collector import collect_all


def test_collect_all():
    result = collect_all()

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
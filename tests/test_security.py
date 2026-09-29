from audit.startup import collect_startup


def test_collect_startup():
    result = collect_startup()

    assert isinstance(result, dict)

    assert "registry_startup" in result
    assert "startup_folders" in result
    assert "boot_logon_scheduled_tasks" in result

    assert isinstance(result["registry_startup"], list)
    assert isinstance(result["startup_folders"], list)
    assert isinstance(
        result["boot_logon_scheduled_tasks"],
        list,
    )
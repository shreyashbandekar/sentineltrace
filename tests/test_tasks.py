from audit.tasks import collect_tasks


def test_collect_tasks():
    result = collect_tasks()

    assert isinstance(result, dict)
    assert "tasks" in result
    assert isinstance(result["tasks"], list)

    for task in result["tasks"]:
        assert "TaskName" in task
        assert "TaskPath" in task
        assert "State" in task
        assert "Author" in task
        assert "Principal" in task
        assert "RunLevel" in task
        assert "LogonType" in task
        assert "Actions" in task
        assert "Triggers" in task
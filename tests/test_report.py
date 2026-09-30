from audit.report import format_report, generate_text_report


def test_formats_report_summary():
    report = {
        "audit_id": "AUDIT-20260925-120000",
        "generated_at": "20260925_120000",
        "metadata": {
            "computer_name": "TEST-PC",
            "username": "test-user",
            "operating_system": "Windows",
            "os_release": "11",
            "os_version": "10.0.26200",
            "architecture": "AMD64",
        },
        "summary": {
            "added": 2,
            "removed": 1,
            "modified": 3,
            "unchanged": 100,
        },
        "investigation": {
            "finding_count": 3,
            "findings": [
                {
                    "section": "services",
                    "change_type": "MODIFIED",
                    "id": "TestService",
                    "details": {
                        "changed_fields": [
                            {
                                "field": "State",
                                "before": "Stopped",
                                "after": "Running",
                            }
                        ]
                    },
                },
                {
                    "section": "services",
                    "change_type": "ADDED",
                    "id": "NewService",
                    "details": {
                        "after": {
                            "Name": "NewService",
                            "State": "Running",
                        }
                    },
                },
                {
                    "section": "services",
                    "change_type": "REMOVED",
                    "id": "OldService",
                    "details": {
                        "before": {
                            "Name": "OldService",
                            "State": "Running",
                        }
                    },
                },
            ],
        },
    }

    output = format_report(report)

    assert "SENTINELTRACE AUDIT REPORT" in output
    assert "Audit ID   : AUDIT-20260925-120000" in output
    assert "Computer Name : TEST-PC" in output
    assert "Username      : test-user" in output
    assert "Operating Sys.: Windows" in output
    assert "OS Version    : 11 (10.0.26200)" in output
    assert "Architecture  : AMD64" in output
    assert "COMPARISON SUMMARY" in output
    assert "Added      : 2" in output
    assert "Removed    : 1" in output
    assert "Modified   : 3" in output
    assert "Unchanged  : 100" in output
    assert "INVESTIGATION SUMMARY" in output
    assert "Total findings : 3" in output


def test_formats_modified_finding():
    report = {
        "generated_at": "20260925_120000",
        "summary": {
            "added": 0,
            "removed": 0,
            "modified": 1,
            "unchanged": 100,
        },
        "investigation": {
            "finding_count": 1,
            "findings": [
                {
                    "section": "services",
                    "change_type": "MODIFIED",
                    "id": "TestService",
                    "details": {
                        "changed_fields": [
                            {
                                "field": "State",
                                "before": "Stopped",
                                "after": "Running",
                            }
                        ]
                    },
                }
            ],
        },
    }

    output = format_report(report)

    assert "[MODIFIED] services: TestService" in output
    assert "State:" in output
    assert "BEFORE: Stopped" in output
    assert "AFTER : Running" in output


def test_formats_added_and_removed_findings():
    report = {
        "generated_at": "20260925_120000",
        "summary": {
            "added": 1,
            "removed": 1,
            "modified": 0,
            "unchanged": 100,
        },
        "investigation": {
            "finding_count": 2,
            "findings": [
                {
                    "section": "services",
                    "change_type": "ADDED",
                    "id": "NewService",
                    "details": {
                        "after": {
                            "Name": "NewService",
                            "State": "Running",
                        }
                    },
                },
                {
                    "section": "services",
                    "change_type": "REMOVED",
                    "id": "OldService",
                    "details": {
                        "before": {
                            "Name": "OldService",
                            "State": "Running",
                        }
                    },
                },
            ],
        },
    }

    output = format_report(report)

    assert "[ADDED] services: NewService" in output
    assert "New item detected." in output
    assert "[REMOVED] services: OldService" in output
    assert "Item no longer present." in output

def test_generate_text_report(tmp_path):
    report_file = tmp_path / "report.json"

    report_file.write_text(
        """
{
    "generated_at": "20260925_120000",
    "summary": {
        "added": 1,
        "removed": 0,
        "modified": 1,
        "unchanged": 100
    },
    "investigation": {
        "finding_count": 1,
        "findings": [
            {
                "section": "services",
                "change_type": "MODIFIED",
                "id": "TestService",
                "details": {
                    "changed_fields": [
                        {
                            "field": "State",
                            "before": "Stopped",
                            "after": "Running"
                        }
                    ]
                }
            }
        ]
    }
}
""",
        encoding="utf-8",
    )

    output = generate_text_report(report_file)

    assert "SENTINELTRACE AUDIT REPORT" in output
    assert "TestService" in output
    assert "BEFORE: Stopped" in output
    assert "AFTER : Running" in output
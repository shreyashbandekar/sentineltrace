import json
import subprocess


def run_powershell(command):
    """Run a PowerShell command and return its output."""
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            command,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


def parse_json(output):
    """Convert PowerShell JSON output into a Python list."""
    if not output:
        return []

    data = json.loads(output)

    if isinstance(data, dict):
        return [data]

    return data


def collect_tasks():
    """Collect Windows Scheduled Tasks and their configuration."""

    command = r"""
Get-ScheduledTask -ErrorAction SilentlyContinue |
ForEach-Object {
    $task = $_

    $info = $null

    try {
        $info = Get-ScheduledTaskInfo `
            -TaskName $task.TaskName `
            -TaskPath $task.TaskPath `
            -ErrorAction Stop
    }
    catch {
        $info = $null
    }

    $actions = @(
        $task.Actions | ForEach-Object {
            [PSCustomObject]@{
                Execute = $_.Execute
                Arguments = $_.Arguments
                WorkingDirectory = $_.WorkingDirectory
            }
        }
    )

    $triggers = @(
        $task.Triggers | ForEach-Object {
            [PSCustomObject]@{
                Type = $_.CimClass.CimClassName
                Enabled = $_.Enabled
                StartBoundary = $_.StartBoundary
                EndBoundary = $_.EndBoundary
                UserId = $_.UserId
            }
        }
    )

    [PSCustomObject]@{
        TaskName = $task.TaskName
        TaskPath = $task.TaskPath
        State = [string]$task.State
        Author = $task.Author
        Description = $task.Description
        Principal = $task.Principal.UserId
        RunLevel = [string]$task.Principal.RunLevel
        LogonType = [string]$task.Principal.LogonType
        Actions = $actions
        Triggers = $triggers
        LastRunTime = if ($info) { $info.LastRunTime } else { $null }
        NextRunTime = if ($info) { $info.NextRunTime } else { $null }
        LastTaskResult = if ($info) { $info.LastTaskResult } else { $null }
    }
} |
Sort-Object TaskPath, TaskName |
ConvertTo-Json -Depth 6 -Compress
"""

    tasks = parse_json(run_powershell(command))

    return {
        "task_count": len(tasks),
        "tasks": tasks,
    }


if __name__ == "__main__":
    task_data = collect_tasks()

    print(
        json.dumps(
            task_data,
            indent=4,
            default=str,
        )
    )
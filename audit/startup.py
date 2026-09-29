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


def collect_startup():
    """Collect programs configured to start automatically."""

    registry_command = r"""
$paths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
)

$results = foreach ($path in $paths) {
    if (Test-Path $path) {
        $properties = Get-ItemProperty $path

        foreach ($property in $properties.PSObject.Properties) {
            if ($property.Name -notmatch "^PS") {
                [PSCustomObject]@{
                    Location = $path
                    Name = $property.Name
                    Command = [string]$property.Value
                }
            }
        }
    }
}

$results |
Sort-Object Location, Name |
ConvertTo-Json -Compress
"""

    startup_folder_command = r"""
$folders = @(
    [Environment]::GetFolderPath("Startup"),
    [Environment]::GetFolderPath("CommonStartup")
)

$results = foreach ($folder in $folders) {
    if ($folder -and (Test-Path $folder)) {
        Get-ChildItem $folder -Force -ErrorAction SilentlyContinue |
        Select-Object `
            @{Name="Location";Expression={$folder}},
            Name,
            FullName,
            Extension,
            Length
    }
}

$results |
Sort-Object Location, Name |
ConvertTo-Json -Compress
"""

    scheduled_startup_command = r"""
Get-ScheduledTask -ErrorAction SilentlyContinue |
Where-Object {
    $_.Triggers.TriggerType -contains "Logon" -or
    $_.Triggers.TriggerType -contains "Boot"
} |
Select-Object `
    TaskName,
    TaskPath,
    State,
    Author,
    Description |
Sort-Object TaskPath, TaskName |
ConvertTo-Json -Compress
"""

    registry_startup = parse_json(
        run_powershell(registry_command)
    )

    startup_folders = parse_json(
        run_powershell(startup_folder_command)
    )

    scheduled_tasks = parse_json(
        run_powershell(scheduled_startup_command)
    )

    return {
        "registry_startup": registry_startup,
        "startup_folders": startup_folders,
        "boot_logon_scheduled_tasks": scheduled_tasks,
    }


if __name__ == "__main__":
    startup = collect_startup()

    print(
        json.dumps(
            startup,
            indent=4,
            default=str,
        )
    )
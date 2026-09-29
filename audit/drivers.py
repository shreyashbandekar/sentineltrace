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


def collect_drivers():
    """Collect installed Windows driver information."""

    command = r"""
Get-CimInstance Win32_SystemDriver -ErrorAction SilentlyContinue |
Select-Object `
    Name,
    DisplayName,
    State,
    StartMode,
    StartName,
    PathName,
    ServiceType |
Sort-Object Name |
ConvertTo-Json -Depth 3 -Compress
"""

    drivers = parse_json(run_powershell(command))

    return {
        "driver_count": len(drivers),
        "drivers": drivers,
    }


if __name__ == "__main__":
    driver_data = collect_drivers()

    print(
        json.dumps(
            driver_data,
            indent=4,
            default=str,
        )
    )
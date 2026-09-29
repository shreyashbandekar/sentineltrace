import json
import subprocess


def collect_services():
    """Collect Windows services and their current state."""

    command = """
Get-CimInstance Win32_Service |
Select-Object Name, DisplayName, State, StartMode, StartName, PathName |
Sort-Object Name |
ConvertTo-Json -Compress
"""

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

    output = result.stdout.strip()

    if not output:
        return []

    services = json.loads(output)

    if isinstance(services, dict):
        services = [services]

    return services


if __name__ == "__main__":
    services = collect_services()

    print(json.dumps({
        "service_count": len(services),
        "services": services,
    }, indent=4, default=str))
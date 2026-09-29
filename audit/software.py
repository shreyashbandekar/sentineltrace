import json
import subprocess


def collect_software():
    """Collect installed Windows applications from registry uninstall entries."""

    command = r"""
$paths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

Get-ItemProperty $paths -ErrorAction SilentlyContinue |
Where-Object { $_.DisplayName } |
Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, InstallLocation |
Sort-Object DisplayName |
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
        error = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(
            f"PowerShell software collection failed "
            f"(exit code {result.returncode}): {error}"
        )

    output = result.stdout.strip()

    if not output:
        return []

    software = json.loads(output)

    if isinstance(software, dict):
        software = [software]

    return software


if __name__ == "__main__":
    software = collect_software()

    print(json.dumps({
        "software_count": len(software),
        "software": software,
    }, indent=4, default=str))
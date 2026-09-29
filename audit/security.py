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
    """Convert PowerShell JSON output into a Python list/object."""
    if not output:
        return []

    data = json.loads(output)

    if isinstance(data, dict):
        return [data]

    return data


def collect_security():
    """Collect important Windows security configuration."""

    defender_command = r"""
Get-MpComputerStatus |
Select-Object `
    AMServiceEnabled,
    AntivirusEnabled,
    AntispywareEnabled,
    RealTimeProtectionEnabled,
    BehaviorMonitorEnabled,
    IoavProtectionEnabled,
    NISEnabled,
    QuickScanAge,
    FullScanAge,
    AntivirusSignatureVersion,
    AntispywareSignatureVersion |
ConvertTo-Json -Compress
"""

    firewall_command = r"""
Get-NetFirewallProfile |
Select-Object `
    Name,
    Enabled,
    DefaultInboundAction,
    DefaultOutboundAction,
    AllowInboundRules,
    AllowLocalFirewallRules,
    AllowLocalIPsecRules |
ConvertTo-Json -Compress
"""

    uac_command = r"""
Get-ItemProperty `
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" |
Select-Object `
    EnableLUA,
    ConsentPromptBehaviorAdmin,
    PromptOnSecureDesktop |
ConvertTo-Json -Compress
"""

    rdp_command = r"""
Get-ItemProperty `
    "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" |
Select-Object fDenyTSConnections |
ConvertTo-Json -Compress
"""

    winrm_command = r"""
Get-Service -Name WinRM -ErrorAction SilentlyContinue |
Select-Object Name, Status, StartType |
ConvertTo-Json -Compress
"""

    remote_assistance_command = r"""
Get-ItemProperty `
    "HKLM:\SYSTEM\CurrentControlSet\Control\Remote Assistance" `
    -ErrorAction SilentlyContinue |
Select-Object fAllowToGetHelp |
ConvertTo-Json -Compress
"""

    defender = parse_json(run_powershell(defender_command))
    firewall = parse_json(run_powershell(firewall_command))
    uac = parse_json(run_powershell(uac_command))
    rdp = parse_json(run_powershell(rdp_command))
    winrm = parse_json(run_powershell(winrm_command))
    remote_assistance = parse_json(
        run_powershell(remote_assistance_command)
    )

    return {
        "windows_defender": defender,
        "firewall_profiles": firewall,
        "uac": uac,
        "remote_desktop": rdp,
        "winrm": winrm,
        "remote_assistance": remote_assistance,
    }


if __name__ == "__main__":
    security = collect_security()

    print(
        json.dumps(
            security,
            indent=4,
            default=str,
        )
    )
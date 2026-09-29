import json
import subprocess


def run_powershell(command):
    """Run a PowerShell command and return its output."""
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
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


def collect_accounts():
    """Collect local Windows user accounts and administrators."""

    users_command = """
Get-LocalUser |
Select-Object Name, Enabled, LastLogon, Description |
ConvertTo-Json -Compress
"""

    admins_command = """
Get-LocalGroupMember -Group "Administrators" |
Select-Object Name, ObjectClass, PrincipalSource |
ConvertTo-Json -Compress
"""

    users_output = run_powershell(users_command)
    admins_output = run_powershell(admins_command)

    users = json.loads(users_output) if users_output else []
    administrators = json.loads(admins_output) if admins_output else []

    if isinstance(users, dict):
        users = [users]

    if isinstance(administrators, dict):
        administrators = [administrators]

    return {
        "users": users,
        "administrators": administrators,
    }


if __name__ == "__main__":
    print(json.dumps(collect_accounts(), indent=4, default=str))
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


def collect_network():
    """Collect network adapters, IP configuration, and active connections."""

    adapters_command = r"""
Get-NetAdapter |
Select-Object Name, InterfaceDescription, Status, MacAddress, LinkSpeed |
ConvertTo-Json -Compress
"""

    ip_command = r"""
Get-NetIPConfiguration |
Select-Object InterfaceAlias, InterfaceIndex, IPv4Address, IPv6Address,
    DNSServer, IPv4DefaultGateway |
ConvertTo-Json -Compress
"""

    connections_command = r"""
Get-NetTCPConnection -ErrorAction SilentlyContinue |
Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort,
    State, OwningProcess |
Sort-Object LocalPort |
ConvertTo-Json -Compress
"""

    adapters_output = run_powershell(adapters_command)
    ip_output = run_powershell(ip_command)
    connections_output = run_powershell(connections_command)

    adapters = json.loads(adapters_output) if adapters_output else []
    ip_configuration = json.loads(ip_output) if ip_output else []
    connections = json.loads(connections_output) if connections_output else []

    if isinstance(adapters, dict):
        adapters = [adapters]

    if isinstance(ip_configuration, dict):
        ip_configuration = [ip_configuration]

    if isinstance(connections, dict):
        connections = [connections]

    return {
        "adapters": adapters,
        "ip_configuration": ip_configuration,
        "tcp_connections": connections,
    }


if __name__ == "__main__":
    network = collect_network()

    print(json.dumps({
        "adapter_count": len(network["adapters"]),
        "ip_configuration_count": len(network["ip_configuration"]),
        "tcp_connection_count": len(network["tcp_connections"]),
        "network": network,
    }, indent=4, default=str))
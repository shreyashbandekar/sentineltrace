import platform
import socket
import getpass
import sys
from datetime import datetime


def collect_system_info():
    """Collect basic system information."""

    return {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "computer_name": socket.gethostname(),
        "username": getpass.getuser(),
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
    }


if __name__ == "__main__":
    import json

    information = collect_system_info()
    print(json.dumps(information, indent=4))
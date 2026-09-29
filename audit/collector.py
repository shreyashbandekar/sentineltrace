import json

from .system_info import collect_system_info
from .accounts import collect_accounts
from .services import collect_services
from .software import collect_software
from .network import collect_network
from .security import collect_security
from .startup import collect_startup
from .tasks import collect_tasks
from .drivers import collect_drivers


def collect_all():
    """Collect a complete snapshot of the laptop."""

    return {
        "system_info": collect_system_info(),
        "accounts": collect_accounts(),
        "services": collect_services(),
        "software": collect_software(),
        "network": collect_network(),
        "security": collect_security(),
        "startup": collect_startup(),
        "scheduled_tasks": collect_tasks(),
        "drivers": collect_drivers(),
    }


if __name__ == "__main__":
    snapshot = collect_all()

    print(
        json.dumps(
            snapshot,
            indent=4,
            default=str,
        )
    )
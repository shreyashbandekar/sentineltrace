def print_header(title):
    print()
    print("=" * 60)
    print(f"{title:^60}")
    print("=" * 60)
    print()


def print_success(message):
    print(f"[+] {message}")


def print_info(message):
    print(f"[*] {message}")


def print_warning(message):
    print(f"[!] {message}")


def print_error(message):
    print(f"[-] {message}")


def print_separator():
    print("-" * 60)
"""
dashboard/admin_panel.py
------------------------
Full-featured CLI Admin Panel for SecureBank.

Features:
1. View system stats (users, accounts, total balance, transactions)
2. List all users
3. Toggle user active/inactive status
4. Freeze/unfreeze accounts
5. Search users by name or email
6. View all recent transactions (last 20)
7. Export stats to report

This runs as a standalone Python script — no browser needed.
Admin must log in with admin credentials first.

Run: python dashboard/admin_panel.py
"""

import requests
import os
import sys
import json
from datetime import datetime

# ─── Config ───────────────────────────────────────────────────────────────────
API_BASE   = "http://localhost:8000"
TOKEN      = None
ADMIN_USER = None


# ─── Colors (ANSI) ────────────────────────────────────────────────────────────
class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"
    DIM    = "\033[2m"

def colored(text, color):
    return f"{color}{text}{C.RESET}"


# ─── Utilities ────────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print(colored("═" * 60, C.BLUE))
    print(colored("   🏦  SecureBank — Admin Control Panel", C.CYAN + C.BOLD))
    if ADMIN_USER:
        print(colored(f"   Logged in as: {ADMIN_USER}", C.DIM))
    print(colored("═" * 60, C.BLUE))


def print_divider():
    print(colored("─" * 60, C.DIM))


def pause():
    input(colored("\n  Press Enter to continue...", C.DIM))


# ─── API Calls ────────────────────────────────────────────────────────────────

def api_get(endpoint):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=5)
        return r.status_code, r.json()
    except requests.RequestException as e:
        return 0, {"error": str(e)}


def api_put(endpoint):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        r = requests.put(f"{API_BASE}{endpoint}", headers=headers, timeout=5)
        return r.status_code, r.json()
    except requests.RequestException as e:
        return 0, {"error": str(e)}


def api_post(endpoint, data):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=5)
        return r.status_code, r.json()
    except requests.RequestException as e:
        return 0, {"error": str(e)}


# ─── Admin Login ──────────────────────────────────────────────────────────────

def admin_login():
    global TOKEN, ADMIN_USER
    clear()
    print_banner()
    print(colored("\n  🔐 Admin Login Required\n", C.YELLOW + C.BOLD))

    email    = input("  Email: ").strip()
    password = input("  Password: ").strip()

    status, data = api_post("/user/login", {"email": email, "password": password})

    if status == 200 and data.get("token"):
        if not data["user"].get("is_admin"):
            print(colored("\n  ✘ You do not have admin privileges.", C.RED))
            sys.exit(1)
        TOKEN      = data["token"]
        ADMIN_USER = data["user"]["name"]
        print(colored(f"\n  ✔ Welcome, {ADMIN_USER}! Login successful.", C.GREEN))
        pause()
    else:
        print(colored(f"\n  ✘ Login failed: {data.get('detail', 'Invalid credentials.')}", C.RED))
        sys.exit(1)


# ─── Feature 1: System Stats ──────────────────────────────────────────────────

def show_stats():
    clear()
    print_banner()
    print(colored("\n  📊 SYSTEM STATISTICS\n", C.CYAN + C.BOLD))

    status, data = api_get("/admin/stats")
    if status != 200:
        print(colored("  ✘ Failed to load stats.", C.RED))
        pause()
        return

    stats = data.get("stats", {})
    u = stats.get("users", {})
    a = stats.get("accounts", {})
    b = stats.get("balance", {})
    t = stats.get("transactions", {})

    print_divider()
    print(f"  {'👥 Users':<30} Total: {colored(u.get('total',0), C.WHITE+C.BOLD)}  |  Active: {colored(u.get('active',0), C.GREEN)}  |  Inactive: {colored(u.get('inactive',0), C.RED)}")
    print(f"  {'🏦 Accounts':<30} Total: {colored(a.get('total',0), C.WHITE+C.BOLD)}")
    print(f"  {'💰 Total Balance in System':<30} {colored(b.get('formatted','₹0'), C.GREEN+C.BOLD)}")
    print_divider()
    print(f"  {'📋 Transactions':<30} Total: {colored(t.get('total',0), C.WHITE+C.BOLD)}")
    print(f"  {'  └ Deposits':<30} {colored(t.get('deposits',0), C.GREEN)}")
    print(f"  {'  └ Withdrawals':<30} {colored(t.get('withdrawals',0), C.YELLOW)}")
    print(f"  {'  └ Transfers':<30} {colored(t.get('transfers',0), C.CYAN)}")
    print_divider()
    pause()


# ─── Feature 2: List All Users ────────────────────────────────────────────────

def list_users():
    clear()
    print_banner()
    print(colored("\n  👥 ALL USERS\n", C.CYAN + C.BOLD))

    status, data = api_get("/admin/users")
    if status != 200:
        print(colored("  ✘ Failed to load users.", C.RED))
        pause()
        return

    users = data.get("users", [])
    if not users:
        print("  No users found.")
        pause()
        return

    print(f"  {'ID':<5} {'Name':<22} {'Email':<28} {'Accounts':<10} {'Status'}")
    print_divider()
    for u in users:
        status_label = colored("● Active", C.GREEN) if u["is_active"] else colored("● Inactive", C.RED)
        admin_badge  = colored(" [ADMIN]", C.YELLOW) if u["is_admin"] else ""
        print(f"  {u['id']:<5} {u['name'][:20]:<22} {u['email'][:26]:<28} {u['accounts']:<10} {status_label}{admin_badge}")

    print_divider()
    print(colored(f"  Total: {len(users)} users", C.DIM))
    pause()


# ─── Feature 3: Toggle User Status ───────────────────────────────────────────

def toggle_user():
    clear()
    print_banner()
    print(colored("\n  🔄 TOGGLE USER STATUS\n", C.CYAN + C.BOLD))

    user_id = input("  Enter User ID to toggle: ").strip()
    if not user_id.isdigit():
        print(colored("  ✘ Invalid ID.", C.RED))
        pause()
        return

    status, data = api_put(f"/admin/users/{user_id}/toggle")
    if status == 200:
        print(colored(f"\n  ✔ {data.get('message')}", C.GREEN))
    else:
        print(colored(f"\n  ✘ {data.get('detail', 'Failed.')}", C.RED))
    pause()


# ─── Feature 4: Freeze Account ───────────────────────────────────────────────

def freeze_account():
    clear()
    print_banner()
    print(colored("\n  🔒 FREEZE / UNFREEZE ACCOUNT\n", C.CYAN + C.BOLD))

    acc = input("  Enter Account Number: ").strip()
    if not acc:
        return

    status, data = api_put(f"/admin/accounts/{acc}/freeze")
    if status == 200:
        print(colored(f"\n  ✔ {data.get('message')}", C.GREEN))
    else:
        print(colored(f"\n  ✘ {data.get('detail', 'Failed.')}", C.RED))
    pause()


# ─── Feature 5: Search User ──────────────────────────────────────────────────

def search_user():
    clear()
    print_banner()
    print(colored("\n  🔍 SEARCH USERS\n", C.CYAN + C.BOLD))

    query = input("  Search (name or email): ").strip()
    if not query:
        return

    status, data = api_get(f"/admin/search?query={query}")
    results = data.get("results", [])

    if not results:
        print(colored("  No matching users found.", C.YELLOW))
    else:
        print(f"\n  {'ID':<6} {'Name':<25} {'Email':<30} {'Active'}")
        print_divider()
        for u in results:
            active = colored("Yes", C.GREEN) if u["is_active"] else colored("No", C.RED)
            print(f"  {u['id']:<6} {u['name'][:23]:<25} {u['email'][:28]:<30} {active}")

    pause()


# ─── Feature 6: Export Stats Report ─────────────────────────────────────────

def export_report():
    clear()
    print_banner()
    print(colored("\n  📄 EXPORT STATS REPORT\n", C.CYAN + C.BOLD))

    status, data = api_get("/admin/stats")
    if status != 200:
        print(colored("  ✘ Cannot fetch stats.", C.RED))
        pause()
        return

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename   = f"data/statements/admin_report_{timestamp}.json"

    os.makedirs("data/statements", exist_ok=True)
    with open(filename, "w") as f:
        json.dump({"generated_at": str(datetime.now()), "stats": data["stats"]}, f, indent=2)

    print(colored(f"\n  ✔ Report saved to: {filename}", C.GREEN))
    pause()


# ─── Main Menu ────────────────────────────────────────────────────────────────

MENU = [
    ("1", "📊 System Statistics",          show_stats),
    ("2", "👥 List All Users",             list_users),
    ("3", "🔄 Toggle User Active Status",  toggle_user),
    ("4", "🔒 Freeze / Unfreeze Account",  freeze_account),
    ("5", "🔍 Search User",                search_user),
    ("6", "📄 Export Stats Report",        export_report),
    ("Q", "🚪 Quit",                       None),
]


def main_menu():
    while True:
        clear()
        print_banner()
        print(colored("\n  ADMIN MENU\n", C.YELLOW + C.BOLD))
        for key, label, _ in MENU:
            print(f"  [{colored(key, C.CYAN + C.BOLD)}]  {label}")
        print()

        choice = input(colored("  → Enter choice: ", C.WHITE)).strip().upper()

        for key, label, fn in MENU:
            if choice == key:
                if fn is None:
                    print(colored("\n  Goodbye, Admin!\n", C.CYAN))
                    sys.exit(0)
                fn()
                break
        else:
            print(colored("  ✘ Invalid option.", C.RED))
            pause()


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    admin_login()
    main_menu()

"""
ui/turtle_ui.py
---------------
A simple desktop banking UI built with Python's Turtle module.
No external libraries needed — runs on any Python 3.x install.

This demonstrates basic UI concepts using Turtle:
- Text rendering
- Simple menu navigation
- Input via turtle.textinput()

Run: python ui/turtle_ui.py
"""

import turtle
import requests

API_BASE = "http://localhost:8000"
TOKEN = None  # Will be set after login


# ─── Screen Setup ─────────────────────────────────────────────────────────────

screen = turtle.Screen()
screen.title("SecureBank — Desktop UI")
screen.bgcolor("#0a1628")
screen.setup(width=700, height=500)
screen.tracer(0)  # Disable auto-update for faster drawing

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)


# ─── Drawing Helpers ──────────────────────────────────────────────────────────

def clear_screen():
    pen.clear()
    screen.update()


def draw_text(text, x=0, y=0, color="white", font=("Courier", 14, "normal"), align="center"):
    pen.penup()
    pen.goto(x, y)
    pen.color(color)
    pen.write(text, align=align, font=font)
    screen.update()


def draw_header():
    draw_text("🏦  S E C U R E B A N K", 0, 200, "#4fc3f7", ("Courier", 22, "bold"))
    draw_text("─" * 50, 0, 175, "#1e3a5f")


def draw_menu():
    clear_screen()
    draw_header()
    options = [
        ("1", "Login"),
        ("2", "Register"),
        ("3", "Check Balance"),
        ("4", "Deposit"),
        ("5", "Withdraw"),
        ("6", "Transfer"),
        ("7", "Transaction History"),
        ("Q", "Quit"),
    ]
    draw_text("MAIN MENU", 0, 140, "#90caf9", ("Courier", 13, "bold"))
    y = 100
    for key, label in options:
        draw_text(f"  [{key}]  {label}", 0, y, "white", ("Courier", 11, "normal"))
        y -= 28


# ─── API Helpers ──────────────────────────────────────────────────────────────

def api_post(endpoint, data):
    global TOKEN
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=data, headers=headers, timeout=5)
        return r.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def api_get(endpoint):
    global TOKEN
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=5)
        return r.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


# ─── Screens ──────────────────────────────────────────────────────────────────

def show_message(msg, color="#80cbc4"):
    """Show a result message at the bottom of screen."""
    pen.penup()
    pen.goto(0, -200)
    pen.color(color)
    pen.write(msg, align="center", font=("Courier", 11, "normal"))
    screen.update()


def screen_login():
    global TOKEN
    email = turtle.textinput("Login", "Enter your email:")
    password = turtle.textinput("Login", "Enter your password:")
    if not email or not password:
        return

    result = api_post("/user/login", {"email": email, "password": password})
    if result.get("token"):
        TOKEN = result["token"]
        show_message(f"✔ Welcome back, {result['user']['name']}!", "#a5d6a7")
    else:
        show_message(f"✘ {result.get('detail', result.get('message', 'Login failed'))}", "#ef9a9a")


def screen_register():
    name  = turtle.textinput("Register", "Full Name:")
    email = turtle.textinput("Register", "Email:")
    pw    = turtle.textinput("Register", "Password:")
    if not all([name, email, pw]):
        return

    result = api_post("/user/register", {"full_name": name, "email": email, "password": pw})
    msg = result.get("message", "Registration done.")
    color = "#a5d6a7" if result.get("success") else "#ef9a9a"
    show_message(f"{'✔' if result.get('success') else '✘'} {msg}", color)


def screen_balance():
    acc = turtle.textinput("Balance Check", "Account Number (e.g., ACC123456789):")
    if not acc:
        return
    result = api_get(f"/transaction/balance/{acc}")
    if result.get("success"):
        show_message(f"Balance: {result['formatted']}", "#80deea")
    else:
        show_message(f"✘ {result.get('detail', 'Error')}", "#ef9a9a")


def screen_deposit():
    acc    = turtle.textinput("Deposit", "Account Number:")
    amount = turtle.textinput("Deposit", "Amount (₹):")
    try:
        result = api_post("/transaction/deposit", {"account_number": acc, "amount": float(amount)})
        msg = result.get("message") or result.get("detail", "Done")
        show_message(f"{'✔' if result.get('success') else '✘'} {msg}")
    except:
        show_message("✘ Invalid amount entered.", "#ef9a9a")


def screen_withdraw():
    acc    = turtle.textinput("Withdraw", "Account Number:")
    amount = turtle.textinput("Withdraw", "Amount (₹):")
    try:
        result = api_post("/transaction/withdraw", {"account_number": acc, "amount": float(amount)})
        msg = result.get("message") or result.get("detail", "Done")
        show_message(f"{'✔' if result.get('success') else '✘'} {msg}")
    except:
        show_message("✘ Invalid amount entered.", "#ef9a9a")


def screen_transfer():
    frm    = turtle.textinput("Transfer", "Your Account Number:")
    to     = turtle.textinput("Transfer", "Recipient Account Number:")
    amount = turtle.textinput("Transfer", "Amount (₹):")
    try:
        result = api_post("/transfer/send", {
            "from_account": frm, "to_account": to, "amount": float(amount)
        })
        msg = result.get("message") or result.get("detail", "Done")
        show_message(f"{'✔' if result.get('success') else '✘'} {msg}")
    except:
        show_message("✘ Error during transfer.", "#ef9a9a")


def screen_history():
    acc = turtle.textinput("History", "Account Number:")
    if not acc:
        return
    result = api_get(f"/transaction/history/{acc}?limit=5")
    if result.get("success"):
        txns = result["transactions"]
        if txns:
            lines = [f"{t['type'].upper()}: {t['formatted']} | {t['date'][:10]}" for t in txns]
            show_message(" | ".join(lines[:3]))
        else:
            show_message("No transactions found.")
    else:
        show_message(f"✘ {result.get('detail', 'Error')}", "#ef9a9a")


# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    draw_menu()

    while True:
        choice = turtle.textinput("SecureBank", "Enter option (1-7 or Q):")
        if not choice:
            continue
        choice = choice.strip().upper()

        if choice == "1":
            screen_login()
        elif choice == "2":
            screen_register()
        elif choice == "3":
            screen_balance()
        elif choice == "4":
            screen_deposit()
        elif choice == "5":
            screen_withdraw()
        elif choice == "6":
            screen_transfer()
        elif choice == "7":
            screen_history()
        elif choice == "Q":
            draw_text("Thank you for using SecureBank. Goodbye!", 0, -150, "#80cbc4")
            screen.update()
            screen.exitonclick()
            break
        else:
            show_message("Invalid option. Enter 1-7 or Q.", "#ffcc80")


if __name__ == "__main__":
    main()

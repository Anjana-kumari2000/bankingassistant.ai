"""
utils/helpers.py
----------------
General-purpose utility functions used across the project.
"""

import random
import string
from datetime import datetime


def generate_account_number() -> str:
    """
    Generates a unique 12-digit account number.
    Format: ACC + 9 random digits  →  e.g., ACC123456789
    """
    digits = ''.join(random.choices(string.digits, k=9))
    return f"ACC{digits}"


def format_currency(amount: float) -> str:
    """
    Formats a float as Indian Rupee string.
    Example: format_currency(10500.5) → "₹10,500.50"
    """
    return f"₹{amount:,.2f}"


def get_current_timestamp() -> str:
    """Returns current datetime as formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_amount(amount: float) -> bool:
    """
    Validates that a transaction amount is positive and reasonable.
    Returns True if valid.
    """
    return 0 < amount <= 10_000_000  # max single transaction: 1 crore


def mask_account_number(account_number: str) -> str:
    """
    Masks account number for display: ACC123456789 → ACC****6789
    """
    if len(account_number) > 7:
        return account_number[:3] + "****" + account_number[-4:]
    return account_number


def log_event(message: str, log_file: str = "data/logs.txt"):
    """
    Appends a timestamped log entry to the log file.
    
    Usage:
        log_event("User john@example.com logged in")
    """
    timestamp = get_current_timestamp()
    entry = f"[{timestamp}] {message}\n"
    with open(log_file, "a") as f:
        f.write(entry)
    print(entry.strip())  # also print to console

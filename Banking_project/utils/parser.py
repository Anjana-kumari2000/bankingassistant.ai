"""
utils/parser.py
---------------
Parses and validates incoming request data.
Used by routes and services to sanitize input before processing.
"""

from typing import Optional


def parse_amount(value) -> Optional[float]:
    """
    Safely converts a value to float (for transaction amounts).
    Returns None if conversion fails.
    
    Examples:
        parse_amount("500")   → 500.0
        parse_amount("abc")   → None
        parse_amount(-100)    → None  (negative not allowed)
    """
    try:
        amount = float(value)
        if amount <= 0:
            return None
        return amount
    except (TypeError, ValueError):
        return None


def parse_account_number(value: str) -> Optional[str]:
    """
    Validates an account number format.
    Must start with "ACC" followed by digits.
    """
    if not isinstance(value, str):
        return None
    value = value.strip().upper()
    if value.startswith("ACC") and value[3:].isdigit() and len(value) == 12:
        return value
    return None


def parse_email(value: str) -> Optional[str]:
    """
    Basic email validation. Returns cleaned email or None.
    """
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    if "@" in value and "." in value.split("@")[-1]:
        return value
    return None


def parse_transaction_filter(params: dict) -> dict:
    """
    Parses query parameters for transaction history filtering.
    
    Accepts:
        - limit: int (default 10, max 100)
        - offset: int (default 0)
        - type: "deposit" | "withdrawal" | "transfer"
    
    Returns cleaned dict of filters.
    """
    filters = {}

    # Limit
    try:
        limit = int(params.get("limit", 10))
        filters["limit"] = min(max(limit, 1), 100)
    except (TypeError, ValueError):
        filters["limit"] = 10

    # Offset
    try:
        offset = int(params.get("offset", 0))
        filters["offset"] = max(offset, 0)
    except (TypeError, ValueError):
        filters["offset"] = 0

    # Transaction type filter
    tx_type = params.get("type", None)
    valid_types = ["deposit", "withdrawal", "transfer"]
    if tx_type in valid_types:
        filters["type"] = tx_type

    return filters

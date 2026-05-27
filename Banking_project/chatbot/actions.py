"""
chatbot/actions.py
------------------
Custom Rasa actions — run when the bot needs to call real backend logic.
Each action connects the chatbot to the FastAPI banking backend via HTTP.

To run the action server:
    rasa run actions --port 5055
"""

import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# FastAPI backend URL
API_BASE = "http://localhost:8000"

# A demo token — in production, pass the user's real JWT
DEMO_TOKEN = "Bearer YOUR_JWT_TOKEN_HERE"
HEADERS = {"Authorization": DEMO_TOKEN}


# ─── Helper ───────────────────────────────────────────────────────────────────

def get_slot(tracker: Tracker, slot_name: str):
    """Retrieves a slot value from the conversation state."""
    return tracker.get_slot(slot_name)


# ─── Action: Check Balance ────────────────────────────────────────────────────

class ActionCheckBalance(Action):
    """
    When user asks for balance, call:
    GET /transaction/balance/{account_number}
    """

    def name(self) -> Text:
        return "action_check_balance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        account_number = get_slot(tracker, "account_number")

        if not account_number:
            dispatcher.utter_message(text="Please provide your account number first.")
            return []

        try:
            response = requests.get(
                f"{API_BASE}/transaction/balance/{account_number}",
                headers=HEADERS, timeout=5
            )
            data = response.json()

            if response.status_code == 200 and data.get("success"):
                dispatcher.utter_message(
                    text=f"Your current balance is {data['formatted']}."
                )
            else:
                dispatcher.utter_message(text=f"Error: {data.get('detail', 'Account not found.')}")

        except requests.RequestException:
            dispatcher.utter_message(text="I'm having trouble connecting to the server. Please try again.")

        return []


# ─── Action: Deposit ──────────────────────────────────────────────────────────

class ActionDeposit(Action):
    def name(self) -> Text:
        return "action_deposit"

    def run(self, dispatcher, tracker, domain):
        account_number = get_slot(tracker, "account_number")
        amount = get_slot(tracker, "amount")

        if not account_number or not amount:
            dispatcher.utter_message(text="I need both your account number and amount to deposit.")
            return []

        try:
            response = requests.post(
                f"{API_BASE}/transaction/deposit",
                json={"account_number": account_number, "amount": float(amount)},
                headers=HEADERS, timeout=5
            )
            data = response.json()
            if response.status_code == 200 and data.get("success"):
                dispatcher.utter_message(text=data["message"])
            else:
                dispatcher.utter_message(text=f"Error: {data.get('detail', 'Deposit failed.')}")
        except requests.RequestException:
            dispatcher.utter_message(text="Server connection failed. Please try again.")

        return []


# ─── Action: Withdraw ─────────────────────────────────────────────────────────

class ActionWithdraw(Action):
    def name(self) -> Text:
        return "action_withdraw"

    def run(self, dispatcher, tracker, domain):
        account_number = get_slot(tracker, "account_number")
        amount = get_slot(tracker, "amount")

        if not account_number or not amount:
            dispatcher.utter_message(text="Please provide your account number and the amount to withdraw.")
            return []

        try:
            response = requests.post(
                f"{API_BASE}/transaction/withdraw",
                json={"account_number": account_number, "amount": float(amount)},
                headers=HEADERS, timeout=5
            )
            data = response.json()
            if response.status_code == 200:
                dispatcher.utter_message(text=data["message"])
            else:
                dispatcher.utter_message(text=f"Error: {data.get('detail', 'Withdrawal failed.')}")
        except requests.RequestException:
            dispatcher.utter_message(text="Server error. Please try again.")

        return []


# ─── Action: Transfer ─────────────────────────────────────────────────────────

class ActionTransfer(Action):
    def name(self) -> Text:
        return "action_transfer"

    def run(self, dispatcher, tracker, domain):
        to_account = get_slot(tracker, "account_number")
        amount = get_slot(tracker, "amount")

        # For simplicity, from_account would come from user's session in real app
        from_account = "ACC_YOUR_ACCOUNT"

        if not to_account or not amount:
            dispatcher.utter_message(text="Please specify the destination account and amount.")
            return []

        try:
            response = requests.post(
                f"{API_BASE}/transfer/send",
                json={"from_account": from_account, "to_account": to_account, "amount": float(amount)},
                headers=HEADERS, timeout=5
            )
            data = response.json()
            if response.status_code == 200:
                dispatcher.utter_message(text=data["message"])
            else:
                dispatcher.utter_message(text=f"Transfer failed: {data.get('detail', 'Unknown error.')}")
        except requests.RequestException:
            dispatcher.utter_message(text="Transfer could not be completed. Server unavailable.")

        return []


# ─── Action: Transaction History ──────────────────────────────────────────────

class ActionTransactionHistory(Action):
    def name(self) -> Text:
        return "action_transaction_history"

    def run(self, dispatcher, tracker, domain):
        account_number = get_slot(tracker, "account_number")
        if not account_number:
            dispatcher.utter_message(text="Which account number would you like the history for?")
            return []

        try:
            response = requests.get(
                f"{API_BASE}/transaction/history/{account_number}?limit=5",
                headers=HEADERS, timeout=5
            )
            data = response.json()
            if response.status_code == 200 and data["transactions"]:
                lines = [f"Last {len(data['transactions'])} transactions:"]
                for t in data["transactions"]:
                    lines.append(f"• {t['type'].upper()}: {t['formatted']} on {t['date'][:10]}")
                dispatcher.utter_message(text="\n".join(lines))
            else:
                dispatcher.utter_message(text="No transactions found for this account.")
        except requests.RequestException:
            dispatcher.utter_message(text="Could not fetch transaction history.")

        return []


# ─── Action: Block Card ───────────────────────────────────────────────────────

class ActionBlockCard(Action):
    def name(self) -> Text:
        return "action_block_card"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="🚨 Your card/account has been flagged for review. "
                 "Please call our helpline at 1800-XXX-XXXX or visit your nearest branch. "
                 "Our team will contact you within 24 hours."
        )
        return []

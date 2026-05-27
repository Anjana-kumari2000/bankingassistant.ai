from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionCheckBalance(Action):
    def name(self) -> Text:
        return "action_check_balance"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Aapka balance ₹25,000 hai 💰")
        return []

class ActionWithdraw(Action):
    def name(self) -> Text:
        return "action_withdraw"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Kitna paisa withdraw karna hai? 💵")
        return []

class ActionDeposit(Action):
    def name(self) -> Text:
        return "action_deposit"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Kitna paisa deposit karna hai? 🏧")
        return []

class ActionTransfer(Action):
    def name(self) -> Text:
        return "action_transfer"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Account number aur amount batayein 🔄")
        return []
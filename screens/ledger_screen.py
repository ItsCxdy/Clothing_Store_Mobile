from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty

class LedgerScreen(MDScreen):
    """
    Screen dedicated to managing trial balances and customer credits/debits.
    """
    db = ObjectProperty(None)
    queries = ObjectProperty(None)

    def set_dependencies(self, db_handler, queries_handler):
        """Method called from main.py to inject DB and Queries objects."""
        self.db = db_handler
        self.queries = queries_handler

    def on_enter(self):
        """Called when the screen becomes the current one."""
        print("Trial Ledger Screen entered.")
        # Logic to load ledger data here
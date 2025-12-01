from kivymd.uix.screen import MDScreen

class InventoryScreen(MDScreen):
    """
    Screen for managing product inventory: viewing stock, adding new products,
    and adjusting stock levels.
    """
    name = 'inventory'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_handler = None
        self.queries = None

    def set_dependencies(self, db_handler, queries):
        """Injects database dependencies."""
        self.db_handler = db_handler
        self.queries = queries
        
    def on_enter(self):
        """Load initial data when screen is entered."""
        print("Inventory Screen entered.")
        # Future implementation: Load all products for display
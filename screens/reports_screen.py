from kivymd.uix.screen import MDScreen

class ReportsScreen(MDScreen):
    """
    Screen for displaying various business reports and analytics.
    """
    name = 'reports' # Corresponds to the navigation item in dashboard.kv

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_handler = None
        self.queries = None

    def set_dependencies(self, db_handler, queries):
        """Injects database dependencies."""
        self.db_handler = db_handler
        self.queries = queries
        
    def on_enter(self):
        """Load report summaries when screen is entered."""
        print("Reports Screen entered.")
        # Future implementation: Load aggregated sales and inventory data
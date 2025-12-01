from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp # Import MDApp to get the running instance
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class DashboardScreen(MDScreen):
    """
    Main landing page after login, displaying key operational statistics.
    """
    db = ObjectProperty(None)
    queries = ObjectProperty(None)

    def set_dependencies(self, db_handler, queries_handler):
        """Method called from main.py to inject DB and Queries objects."""
        self.db = db_handler
        self.queries = queries_handler
        
    def on_enter(self, *args):
        """
        Called when the screen becomes visible.
        Schedules the update of statistics and navigation drawer.
        """
        # Ensure the UI update happens after the widget is fully built
        Clock.schedule_once(self.update_ui, 0)
        
    def update_ui(self, dt):
        """Fetches data from the database and updates the dashboard UI (Fix 3 Implementation)."""
        
        # FIX: Get the running app instance correctly
        app = MDApp.get_running_app()
        
        # 1. Update Title (Fix 2: Uses the new ID 'dashboard_title')
        if 'dashboard_title' in self.ids and app.user_role:
            self.ids.dashboard_title.title = f"Dashboard - Role: {app.user_role.capitalize()}"
        
        # 2. Update Stats (Fix 3: Populating data from DB)
        if self.queries:
            sales_today = self.queries.get_total_sales_for_today()
            pending_trials_count = self.queries.get_pending_trials_count()
        else:
            # Fallback for development if queries object is not yet set
            sales_today = 0.00
            pending_trials_count = 0

        # Update UI Labels
        if 'sales_today' in self.ids:
            # Format sales to two decimal places with comma separation
            self.ids.sales_today.text = f"${sales_today:,.2f}"
        
        if 'pending_trials' in self.ids:
            self.ids.pending_trials.text = f"{pending_trials_count} items"

    def logout(self):
        """Resets user state and navigates back to the login screen."""
        app = MDApp.get_running_app()
        app.user = None
        app.user_role = None
        self.manager.current = 'login'
        self.manager.transition.direction = 'right'
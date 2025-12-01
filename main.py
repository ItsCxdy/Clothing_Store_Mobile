import os
from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
# Import the Kivy Builder to manually load .kv files
from kivy.lang import Builder 
from kivy.core.window import Window # Import Window to set initial size

# Set the default window size (often helps prevent blank screens on initial run)
Window.size = (400, 700) 

# 1. Database and Query Imports
from database.db_handler import DatabaseHandler
from database.queries import Queries

# 2. Screen Imports
from screens.login_screen import LoginScreen
from screens.dashboard import DashboardScreen
from screens.inventory import InventoryScreen
from screens.billing_screen import BillingScreen as PosScreen 
from screens.ledger_screen import LedgerScreen
from screens.reports_screen import ReportsScreen

class ClothingStoreApp(MDApp):
    """
    Main KivyMD application class.
    Handles theme setup, database initialization, and screen management.
    """
    db = None
    queries = None
    
    # User state properties
    user = None
    user_role = None

    def build(self):
        # Set the application theme and colors
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "LightBlue"
        self.theme_cls.theme_style = "Light" 

        # --- 1. Load All KV Files Explicitly ---
        kv_files_dir = os.path.join(os.path.dirname(__file__), "screens")
        kv_files = [f for f in os.listdir(kv_files_dir) if f.endswith(".kv")]
        
        for kv_file in kv_files:
            try:
                # Ensure correct path is used for loading
                Builder.load_file(os.path.join(kv_files_dir, kv_file))
                print(f"[KV Loader] Loaded: {kv_file}")
            except Exception as e:
                print(f"[KV ERROR] Failed to load {kv_file}: {e}")
                
        # --- 2. Database Initialization ---
        self._initialize_database()

        # --- 3. Screen Manager Setup ---
        sm = ScreenManager()
        
        # Instantiate all screens
        login_screen = LoginScreen(name='login')
        dashboard_screen = DashboardScreen(name='dashboard')
        inventory_screen = InventoryScreen(name='inventory')
        pos_screen = PosScreen(name='pos')
        ledger_screen = LedgerScreen(name='ledger')
        reports_screen = ReportsScreen(name='reports')
        
        # Inject dependencies into screens
        screens = [login_screen, dashboard_screen, inventory_screen, pos_screen, ledger_screen, reports_screen]
        for screen in screens:
            screen.set_dependencies(self.db, self.queries)

        # Add screens to the manager
        sm.add_widget(login_screen)
        sm.add_widget(dashboard_screen)
        sm.add_widget(inventory_screen)
        sm.add_widget(pos_screen)
        sm.add_widget(ledger_screen)
        sm.add_widget(reports_screen)

        # Start on the login screen
        sm.current = 'login'
        return sm

    def _initialize_database(self):
        """Initializes the database connection and queries."""
        # Use a path within the app's standard data directory
        db_path = os.path.join(self.user_data_dir, 'store.db')
        
        # Instantiate the database handler
        self.db = DatabaseHandler(db_path)
        
        # Create tables and initial data (if needed)
        self.db.setup_database()
        
        # Instantiate the high-level queries interface
        self.queries = Queries(self.db)
        
    def on_stop(self):
        """Called when the application stops."""
        if self.db:
            self.db.close()
            print("[INFO] Database connection closed.")
            
if __name__ == '__main__':
    ClothingStoreApp().run()
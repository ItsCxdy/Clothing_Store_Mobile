import datetime
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.properties import ObjectProperty

class LoginScreen(MDScreen):
    """
    Handles user authentication logic.
    Inherits from MDScreen (Fix 6: Consistent screen inheritance).
    """
    db = ObjectProperty(None)
    queries = ObjectProperty(None)
    
    def set_dependencies(self, db_handler, queries_handler):
        """Method called from main.py to inject DB and Queries objects."""
        self.db = db_handler
        self.queries = queries_handler

    def attempt_login(self):
        """
        Attempts to authenticate the user using provided credentials.
        The method name is updated to match the KV call (Fix 1).
        """
        # Using MDApp.get_running_app() for robustness
        app = MDApp.get_running_app() 
        
        # Accessing IDs as per the new KV structure (Fix 1)
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        error_label = self.ids.error_label

        if not username or not password:
            error_label.text = "Username and password are required."
            return

        user_data = self.queries.get_user_by_credentials(username, password)
        
        if user_data:
            # Successful Login
            app.user = user_data
            app.user_role = user_data['role']
            
            # Reset fields and errors
            self.ids.username_input.text = ""
            self.ids.password_input.text = ""
            error_label.text = ""

            # Navigate to Dashboard
            self.manager.current = 'dashboard'
            self.manager.transition.direction = 'left' # Added transition for better UX
        else:
            # Failed Login
            error_label.text = "Invalid username or password."
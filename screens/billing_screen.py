# screens/billing_screen.py

from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivymd.uix.list import TwoLineListItem
from kivymd.app import MDApp
from kivy.clock import Clock # Used for debounce/scheduling

class BillingScreen(MDScreen):
    """
    Screen dedicated to Point of Sale (POS) operations (imported as PosScreen in main.py).
    """
    db = ObjectProperty(None)
    queries = ObjectProperty(None)
    
    # State Management for POS
    search_query = StringProperty("")
    # Stores items as a list of dictionaries: [{'id': 101, 'name': 'T-Shirt', 'price': 19.99, 'qty': 1, 'total': 19.99}]
    cart_items = ListProperty([])
    # Search results for product list
    search_results = ListProperty([])
    
    def set_dependencies(self, db_handler, queries_handler):
        """Method called from main.py to inject DB and Queries objects."""
        self.db = db_handler
        self.queries = queries_handler
        self.reset_cart()
        
    def on_enter(self):
        """Called when the screen becomes the current one."""
        print("Billing/POS Screen entered.")
        
    def reset_cart(self):
        """Clears the current transaction cart."""
        self.cart_items = []
        
    def add_item_to_cart(self, product_data):
        """Adds a selected item to the cart, handling quantity updates."""
        
        # We need to create a deep copy of cart_items to modify and reassign
        # it, which correctly triggers the Kivy ListProperty update.
        temp_cart = list(self.cart_items)
        found = False
        
        # Check if the item is already in the cart
        for item in temp_cart:
            # Assuming product_data has a unique identifier like 'id'
            if item['id'] == product_data['id']:
                if item.get('stock_quantity', 0) < item['qty'] + 1:
                    print(f"Cannot add more {item['name']}: low stock ({item.get('stock_quantity')})")
                    return
                item['qty'] += 1
                item['total'] = round(item['qty'] * item['price'], 2)
                found = True
                break
                
        if not found:
            stock_qty = product_data.get('stock_quantity', 0)
            if stock_qty < 1:
                print(f"Out of stock: {product_data.get('name')}")
                return
            # Add new item
            new_item = {
                'id': product_data.get('id', 0),
                'name': product_data.get('name', 'Unknown Product'),
                'price': round(product_data.get('sell_price', 0.0), 2),
                'qty': 1,
                'total': round(product_data.get('sell_price', 0.0), 2),
                'stock_quantity': stock_qty,
            }
            temp_cart.append(new_item)
            
        # Reassign the temporary list to trigger the Kivy ListProperty update
        self.cart_items = temp_cart
        
        print(f"Item added: {product_data.get('name')}. Current items in cart: {len(self.cart_items)}")
        
    def get_cart_total(self):
        """Calculates the total price of all items in the cart."""
        total = sum(item['total'] for item in self.cart_items)
        return f"${total:.2f}"


    def process_search(self, query):
        """
        Handles the product search input using debounce.
        """
        self.search_query = query
        # Cancel any previous scheduled search
        Clock.unschedule(self._perform_search)
        # Schedule the search to run after 0.5 seconds of no new input
        Clock.schedule_once(self._perform_search, 0.5)

    def _perform_search(self, dt):
        """Performs the actual product search based on search_query."""
        if self.search_query and self.queries:
            results = self.queries.search_products(self.search_query)
            
            print(f"Search results for '{self.search_query}': {len(results)} found.")
            
            # Auto-add if exact match (e.g., successful SKU scan)
            if len(results) == 1:
                self.add_item_to_cart(results[0])
                # Clear search query field after successful scan/match
                self.ids.search_input.text = ""
            
            self.search_results = results
        
    def complete_transaction(self):
        """Completes the real sale transaction."""
        if not self.cart_items:
            print("Cannot complete transaction: Cart is empty.")
            return
        
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if not app.user or 'id' not in app.user:
            print("No logged in user.")
            return
        
        total_amount = sum(item['total'] for item in self.cart_items)
        items_list = [(item['id'], item['qty'], item['price']) for item in self.cart_items]
        payment_method = "Cash"  # TODO: Add payment method selector
        user_id = app.user['id']
        
        transaction_id = self.queries.create_transaction(
            total_amount, payment_method, user_id, items_list
        )
        if transaction_id:
            print(f"Transaction #{transaction_id} completed! Total: ${total_amount:.2f}")
            self.reset_cart()
        else:
            print("Transaction failed (e.g., insufficient stock or DB error).")
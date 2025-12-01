import datetime
import sqlite3

class Queries:
    """
    Centralized class for all high-level database operations,
    using the DatabaseHandler object.
    (Fix 8: Removed the __main__ test block to prevent DB pollution.)
    """
    def __init__(self, db_handler):
        self.db = db_handler

    # --- User Queries ---

    def get_user_by_credentials(self, username, password):
        """
        Retrieves user data by username and password.
        Returns a dict of user details or None.
        """
        query = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"
        # execute_query is set up to return dicts now
        return self.db.execute_query(query, (username, password), fetch_one=True)

    # --- Dashboard Queries (Fix 3 Implementation) ---
    
    def get_total_sales_for_today(self):
        """
        Calculates the total sales amount for the current date.
        """
        # ISO 8601 format compatible with SQLite DATETIME column
        today_start = datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
        query = "SELECT SUM(total_amount) FROM transactions WHERE timestamp >= ?"
        
        # We fetch raw data here as it's a SUM, not a row object
        result = self.db.execute_query(query, (today_start,), fetch_one=True) 
        # Check if result is a dict (from handler) or raw tuple/list
        if isinstance(result, dict) and 'SUM(total_amount)' in result:
             return result['SUM(total_amount)'] if result['SUM(total_amount)'] is not None else 0.0
        elif isinstance(result, tuple) and result[0] is not None:
             return result[0]
        return 0.0


    def get_pending_trials_count(self):
        """
        Counts the number of items currently marked as 'On_Trial'.
        """
        query = "SELECT COUNT(id) FROM trial_ledger WHERE status = 'On_Trial'"
        
        # We fetch raw data here as it's a COUNT, not a row object
        result = self.db.execute_query(query, fetch_one=True)
        
        if isinstance(result, dict) and 'COUNT(id)' in result:
             return result['COUNT(id)'] if result['COUNT(id)'] is not None else 0
        elif isinstance(result, tuple) and result[0] is not None:
             return result[0]
        return 0


    # --- Product/Inventory Queries ---

    def get_product_by_sku(self, sku):
        """Retrieves a single product by SKU."""
        query = "SELECT * FROM products WHERE sku = ?"
        return self.db.execute_query(query, (sku,), fetch_one=True)

    def update_product_stock(self, product_id, quantity_change):
        """
        Updates the stock quantity for a product. 
        
        :param product_id: ID of the product.
        :param quantity_change: The amount to add (positive) or subtract (negative).
        
        (Fix 12: Using a single atomic update statement to prevent stock from going below zero, 
        which addresses the oversell risk in a non-concurrent environment.)
        """
        query = """
        UPDATE products 
        SET stock_quantity = stock_quantity + ? 
        WHERE id = ? 
        AND (stock_quantity + ?) >= 0;
        """
        # The WHERE condition prevents stock from going below zero if we are decrementing.
        return self.db.execute_query(query, (quantity_change, product_id, quantity_change))

    # --- Transaction Queries ---

    def create_transaction(self, total_amount, payment_method, user_id, items_list):
        """
        Creates a new transaction and related transaction items (atomic operation).
        
        :param total_amount: Total sale amount.
        :param payment_method: How the customer paid.
        :param user_id: ID of the user (salesperson) who made the sale.
        :param items_list: List of tuples (product_id, quantity, price_at_sale).
        """
        # Must manually manage cursor/connection for atomic operations
        try:
            # 1. Insert Transaction Header
            transaction_query = "INSERT INTO transactions (total_amount, payment_method, user_id) VALUES (?, ?, ?)"
            self.db.cursor.execute(transaction_query, (total_amount, payment_method, user_id))
            transaction_id = self.db.cursor.lastrowid
            
            # 2. Insert Transaction Items and Update Stock
            for product_id, quantity, price_at_sale in items_list:
                # Insert item details
                item_query = "INSERT INTO transaction_items (transaction_id, product_id, quantity, price_at_sale) VALUES (?, ?, ?, ?)"
                self.db.cursor.execute(item_query, (transaction_id, product_id, quantity, price_at_sale))
                
                # Update stock (decrement stock)
                self.update_product_stock(product_id, -quantity)
            
            # 3. Commit all changes
            self.db.conn.commit()
            return transaction_id
        
        except sqlite3.Error as e:
            self.db.conn.rollback()
            print(f"[DB ERROR] Transaction failed: {e}")
            return None

    # --- Trial Ledger Queries ---

    def checkout_for_trial(self, customer_name, customer_phone, product_id):
        """Registers a product checked out for trial."""
        query = "INSERT INTO trial_ledger (customer_name, customer_phone, product_id, status) VALUES (?, ?, ?, 'On_Trial')"
        return self.db.execute_query(query, (customer_name, customer_phone, product_id))
        
    def get_on_trial_items(self):
        """
        Retrieves all items currently on trial, joined with product details.
        """
        query = """
        SELECT 
            tl.id, tl.customer_name, tl.customer_phone, tl.date_taken, 
            p.name, p.size, p.color, p.sell_price, p.id as product_id
        FROM trial_ledger tl
        JOIN products p ON tl.product_id = p.id
        WHERE tl.status = 'On_Trial'
        ORDER BY tl.date_taken DESC;
        """
        return self.db.execute_query(query, fetch_all=True)

    def update_trial_status(self, ledger_id, new_status):
        """Updates the status of a specific trial ledger entry."""
        query = "UPDATE trial_ledger SET status = ? WHERE id = ?"
        return self.db.execute_query(query, (new_status, ledger_id))
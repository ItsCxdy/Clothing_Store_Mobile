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

    def search_products(self, query):
        """
        Fuzzy search for products by name or SKU.
        Returns list of product dicts with relevant fields.
        """
        if not query:
            return []
        search_term = f'%{query.lower()}%'
        sql = """
        SELECT id, name, sku, sell_price, stock_quantity, size, color
        FROM products
        WHERE LOWER(name) LIKE ? OR LOWER(sku) LIKE ?
        ORDER BY name ASC
        LIMIT 20
        """
        results = self.db.execute_query(sql, (search_term, search_term), fetch_all=True)
        return results or []

    # --- Transaction Queries ---

    def create_transaction(self, total_amount, payment_method, user_id, items_list):
        """
        Creates a new transaction and related transaction items (fully atomic).
        Checks stock before updating, direct cursor ops, single commit.
        """
        try:
            # 1. Insert Transaction Header
            transaction_query = "INSERT INTO transactions (total_amount, payment_method, user_id) VALUES (?, ?, ?)"
            self.db.cursor.execute(transaction_query, (total_amount, payment_method, user_id))
            transaction_id = self.db.cursor.lastrowid
            
            # 2. For each item: check stock, insert item, update stock
            for product_id, quantity, price_at_sale in items_list:
                # Check sufficient stock
                check_query = "SELECT stock_quantity FROM products WHERE id = ?"
                self.db.cursor.execute(check_query, (product_id,))
                stock_row = self.db.cursor.fetchone()
                if not stock_row or stock_row[0] < quantity:
                    raise sqlite3.Error(f"Insufficient stock for product {product_id}: {stock_row[0] if stock_row else 0} < {quantity}")
                
                # Insert item details
                item_query = "INSERT INTO transaction_items (transaction_id, product_id, quantity, price_at_sale) VALUES (?, ?, ?, ?)"
                self.db.cursor.execute(item_query, (transaction_id, product_id, quantity, price_at_sale))
                
                # Update stock atomically (direct cursor, no intermediate commit)
                update_query = "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?"
                self.db.cursor.execute(update_query, (quantity, product_id))
            
            # 3. Single commit for all ops
            self.db.conn.commit()
            print(f"[DB] Transaction {transaction_id} committed successfully.")
            return transaction_id
        
        except sqlite3.Error as e:
            self.db.conn.rollback()
            print(f"[DB ERROR] Transaction failed (rolled back): {e}")
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
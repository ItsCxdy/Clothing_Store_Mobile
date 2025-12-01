import sqlite3
import os

class DatabaseHandler:
    """
    Handles connection, execution, and closing of the SQLite database.
    """
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """Establishes the connection and cursor."""
        try:
            # Set the thread check to False for Kivy usage (not strictly necessary but safer)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row # Use Row factory for dictionary-like access
            self.cursor = self.conn.cursor()
            print(f"[DB] Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Connection failed: {e}")

    def close(self):
        """Closes the connection."""
        if self.conn:
            self.conn.close()
            
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
        """Executes a query and optionally fetches results."""
        if not self.conn:
            print("[DB ERROR] Database not connected.")
            return None

        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # Auto-commit for DML statements
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.conn.commit()
            
            if fetch_one:
                # Return result as dict for consistency
                result = self.cursor.fetchone()
                return dict(result) if result else None
            elif fetch_all:
                # Return results as list of dicts
                results = self.cursor.fetchall()
                return [dict(row) for row in results]
            else:
                return True
        except sqlite3.Error as e:
            # Important: Rollback if an error occurs during an uncommitted transaction
            if self.conn:
                self.conn.rollback()
            print(f"[DB ERROR] Query failed: {e}\nQuery: {query}\nParams: {params}")
            return None

    def setup_database(self):
        """Creates all necessary tables and ensures default data exists."""
        # Fix 4: Changed to CREATE IF NOT EXISTS to prevent destructive drops
        self._create_users_table()
        self._create_products_table()
        self._create_vendors_table()
        self._create_transactions_table()
        self._create_transaction_items_table()
        self._create_trial_ledger_table()
        
        self._ensure_admin_user()

    def _create_users_table(self):
        """
        Creates the 'users' table if it does not exist.
        (Fix 4 implemented here: using IF NOT EXISTS).
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL, 
            role TEXT NOT NULL 
        );
        """
        self.execute_query(create_table_query)

    def _ensure_admin_user(self):
        """Ensures the default 'admin' user exists."""
        default_username = 'admin'
        default_password = 'adminpass' 
        
        check_query = "SELECT id FROM users WHERE username = ?"
        user_exists = self.execute_query(check_query, (default_username,), fetch_one=True)
        
        if not user_exists:
            insert_query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            self.execute_query(insert_query, (default_username, default_password, 'admin'))
            print(f"[DB] Inserting default admin user ({default_username}/{default_password}).")
            
    def _create_products_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            vendor_id INTEGER,
            sku TEXT UNIQUE,
            buy_price REAL NOT NULL,
            sell_price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL,
            size TEXT,
            color TEXT,
            FOREIGN KEY (vendor_id) REFERENCES vendors(id)
        );
        """
        self.execute_query(create_table_query)

    def _create_vendors_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            contact_person TEXT,
            phone TEXT
        );
        """
        self.execute_query(create_table_query)

    def _create_transactions_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            payment_method TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        self.execute_query(create_table_query)

    def _create_transaction_items_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transaction_items (
            id INTEGER PRIMARY KEY,
            transaction_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            price_at_sale REAL NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        """
        self.execute_query(create_table_query)

    def _create_trial_ledger_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS trial_ledger (
            id INTEGER PRIMARY KEY,
            customer_name TEXT,
            customer_phone TEXT,
            product_id INTEGER NOT NULL,
            date_taken DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL, -- 'On_Trial', 'Returned', 'Purchased'
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        """
        self.execute_query(create_table_query)
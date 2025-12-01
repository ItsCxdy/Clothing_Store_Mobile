class Product:
    """
    Represents an individual clothing item (Product) in the inventory.
    This class includes all necessary fields for inventory management and sales.
    """
    def __init__(self, id: int = None, vendor_id: int = None, name: str = None, 
                 barcode: str = None, size: str = None, color: str = None, 
                 buy_price: float = 0.0, sell_price: float = 0.0, stock_quantity: int = 0):
        """
        Initializes a Product object.

        :param id: Primary key ID.
        :param vendor_id: Foreign key to the Vendor table.
        :param name: Product name (e.g., 'Slim Fit Jeans').
        :param barcode: Unique identifier, used for quick scanning.
        :param size: Clothing size (e.g., 'S', '32', 'OS').
        :param color: Product color.
        :param buy_price: Cost price (for profit calculation).
        :param sell_price: Retail price.
        :param stock_quantity: Current quantity in stock.
        """
        self.id = id
        self.vendor_id = vendor_id
        self.name = name
        self.barcode = barcode
        self.size = size
        self.color = color
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.stock_quantity = stock_quantity

    def to_tuple(self):
        """
        Converts the model object into a tuple suitable for insertion 
        via Queries.add_new_product().
        Order must match the SQL in queries.py.
        """
        return (self.vendor_id, self.name, self.barcode, self.size, self.color, 
                self.buy_price, self.sell_price, self.stock_quantity)

    @classmethod
    def from_db_row(cls, row: tuple, full_details=True):
        """
        Creates a Product object from a database result row.
        
        If full_details=True (8 fields from Product table):
        (id, vendor_id, name, barcode, size, color, buy_price, sell_price, stock_quantity)
        
        If full_details=False (for search results):
        (id, name, barcode, size, sell_price, stock_quantity, vendor_name)
        """
        if full_details and len(row) >= 9:
             return cls(id=row[0], vendor_id=row[1], name=row[2], barcode=row[3], size=row[4], 
                        color=row[5], buy_price=row[6], sell_price=row[7], stock_quantity=row[8])
        
        # Handle partial data from search_products query (7 fields)
        elif not full_details and len(row) == 7:
            # Note: vendor_id, color, and buy_price are missing here, set to None/0.0
            p = cls(id=row[0], name=row[1], barcode=row[2], size=row[3], sell_price=row[4], stock_quantity=row[5])
            p.vendor_name = row[6] # Add vendor_name property for display
            return p

        return None

    def __repr__(self):
        return f"Product(id={self.id}, name='{self.name}', barcode='{self.barcode}', stock={self.stock_quantity})"
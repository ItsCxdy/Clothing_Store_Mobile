class TrialLedgerEntry:
    """
    Represents an entry in the Trial Ledger (New Feature).
    Tracks items that have been taken out by a customer without immediate payment.
    """
    STATUS_ON_TRIAL = 'On_Trial'
    STATUS_RETURNED = 'Returned'
    STATUS_PURCHASED = 'Purchased'

    def __init__(self, id: int = None, customer_name: str = None, customer_phone: str = None,
                 product_id: int = None, date_taken: str = None, status: str = STATUS_ON_TRIAL,
                 product_name: str = None, product_price: float = 0.0):
        """
        Initializes a Trial Ledger Entry object.

        :param id: Primary key ID.
        :param customer_name: Name of the customer who took the item.
        :param customer_phone: Customer contact for follow-up.
        :param product_id: ID of the item taken.
        :param date_taken: Timestamp of checkout.
        :param status: Current status ('On_Trial', 'Returned', 'Purchased').
        :param product_name: Name of the product (fetched via JOIN).
        :param product_price: Sell price of the product (fetched via JOIN).
        """
        self.id = id
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.product_id = product_id
        self.date_taken = date_taken
        self.status = status
        
        # Denormalized fields for UI display (from JOIN query in queries.py)
        self.product_name = product_name
        self.product_price = product_price 

    def to_tuple(self):
        """
        Converts the model object into a tuple for insertion.
        Used by Queries.checkout_for_trial().
        """
        return (self.customer_name, self.customer_phone, self.product_id) # date_taken and status are added in queries.py

    @classmethod
    def from_db_row(cls, row: tuple):
        """
        Creates a TrialLedgerEntry object from a database result row.
        Assumes the row comes from Queries.get_on_trial_items():
        (tl.id, tl.customer_name, tl.customer_phone, tl.date_taken, p.name, p.size, p.color, p.sell_price, p.id as product_id)
        """
        if len(row) == 9:
            # Extract data from the joined query result
            ledger_id, cust_name, cust_phone, date_taken, prod_name, size, color, sell_price, product_id = row
            
            # Combine name, size, and color for a display friendly name
            full_name = f"{prod_name} ({color}/{size})"

            return cls(
                id=ledger_id,
                customer_name=cust_name,
                customer_phone=cust_phone,
                product_id=product_id,
                date_taken=date_taken,
                status=cls.STATUS_ON_TRIAL, # Status is known to be 'On_Trial' based on the query
                product_name=full_name,
                product_price=sell_price
            )
        return None

    def __repr__(self):
        return f"TrialLedgerEntry(id={self.id}, customer='{self.customer_name}', item='{self.product_name}', status='{self.status}')"
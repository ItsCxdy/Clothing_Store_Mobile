class Vendor:
    """
    Represents a Vendor (supplier) in the Clothing Store application.
    This class is used to structure data fetched from the database
    and to pass structured data to the Queries layer for insertion/update.
    """
    def __init__(self, id: int = None, name: str = None, contact_info: str = None, total_items_supplied: int = 0):
        """
        Initializes a Vendor object.

        :param id: Primary key ID (None for new vendors).
        :param name: Vendor company name (required).
        :param contact_info: Contact details (e.g., phone, email).
        :param total_items_supplied: Calculated field from the DB (read-only for model).
        """
        self.id = id
        self.name = name
        self.contact_info = contact_info
        self.total_items_supplied = total_items_supplied

    def to_tuple(self, include_id=False):
        """
        Converts the model object into a tuple for database insertion/update.
        Excludes ID by default, as SQLite handles auto-increment.
        """
        data = (self.name, self.contact_info)
        if include_id and self.id is not None:
            return data + (self.id,)
        return data

    @classmethod
    def from_db_row(cls, row: tuple):
        """
        Creates a Vendor object from a database result row.
        Assumes the DB query returns fields in this order:
        (id, name, contact_info, total_items_supplied)
        """
        if len(row) == 4:
            return cls(id=row[0], name=row[1], contact_info=row[2], total_items_supplied=row[3])
        # Handle simple fetch (e.g., SELECT id, name)
        elif len(row) == 2:
            return cls(id=row[0], name=row[1])
        return None

    def __repr__(self):
        return f"Vendor(id={self.id}, name='{self.name}', contact='{self.contact_info[:20]}...')"
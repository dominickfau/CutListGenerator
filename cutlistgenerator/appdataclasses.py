import datetime
from dataclasses import dataclass
from typing import Optional, List

from cutlistgenerator.error import ProductNotInKitException
from cutlistgenerator.database import CutListDatabase, MySQLDatabaseConnection


@dataclass
class Product:
    """Represents a product."""

    database_connection: CutListDatabase
    number: str
    description: str
    uom: str
    unit_price_dollars: Optional[float] = None
    kit_flag: bool = False
    parent_kit_product: Optional['Product'] = None
    id: int = None

    def __post_init__(self):
        """Initialize the product after it's been created."""
        
        if self.kit_flag and self.parent_kit_product is None:
            raise ProductNotInKitException("Product is marked as a kit but does not have a parent kit product number.")

        if self.unit_price_dollars is None:
            self.unit_price_dollars = 0.0

    @classmethod
    def from_dict(cls, database_connection: CutListDatabase, product_dict: dict):
        """Creates a product from a dictionary."""

        return cls(database_connection, **product_dict)

    @classmethod
    def from_number(cls, database_connection: CutListDatabase, number: str) -> 'Product':
        """Returns a product from the database by its number. Returns None if not found."""

        data = database_connection.get_product_by_number(number)
        if not data:
            return None

        parent_kit_product_number = data.pop('parent_kit_product_number', None)

        return cls(database_connection, **data)
    
    def set_parent_kit_product(self, parent_kit_product: 'Product'):
        """Sets the parent kit product for this product."""

        self.parent_kit_product = parent_kit_product
        self.kit_flag = True
    
    def save(self):
        """Saves the product to the database."""

        self.id = self.database_connection.save_product(self)


@dataclass
class WireCutterOption:
    """Represents a wire cutter option."""

    database_connection: CutListDatabase
    name: str
    description: Optional[str] = None
    id: int = None
    
    @classmethod
    def from_dict(cls, database_connection: CutListDatabase, wire_cutter_option_dict: dict):
        """Creates a wire cutter option from a dictionary."""

        return cls(database_connection, **wire_cutter_option_dict)

    @classmethod
    def from_number(cls, database_connection: CutListDatabase, name: str) -> 'WireCutterOption':
        """Returns a wire cutter option from the database by its name."""

        return cls(database_connection, **database_connection.get_wire_cutter_option_by_name(name))

    def save(self):
        """Saves the wire cutter option to the database."""

        self.id = self.database_connection.save_wire_cutter_option(self.__dict__)


@dataclass
class WireCutter:
    """Represents a wire cutter."""

    database_connection: CutListDatabase
    name: str
    max_wire_gauge_awg: int
    processing_speed_feet_per_minute: Optional[int] = None
    details: Optional[str] = None
    options: Optional[List[WireCutterOption]] = None
    id: int = None

    def __post_init__(self):
        """Initialize the wire cutter after it's been created."""

        if self.options is None:
            self.options = []

    @classmethod
    def from_dict(cls, database_connection: CutListDatabase, wire_cutter_dict: dict):
        """Creates a wire cutter from a dictionary."""
        
        return cls(database_connection, **wire_cutter_dict)

    @classmethod
    def from_name(cls, database_connection: CutListDatabase, name: str) -> 'WireCutter':
        """Returns a wire cutter from the database by its name."""

        return cls(database_connection, **database_connection.get_wire_cutter_by_name(name))

    def add_option(self, option: WireCutterOption):
        """Add a wire cutter option to this wire cutter. If the option already exists, it will be updated."""

        if option not in self.options:
            self.options.append(option)
        else:
            for existing_option in self.options:
                if existing_option != option:
                    continue

                existing_option = option
                break
    
    def remove_option(self, option: WireCutterOption):
        """Remove a wire cutter option from this wire cutter. If the option does not exist, it will be ignored."""

        if option in self.options:
            self.options.remove(option)
    
    def set_details(self, details: str):
        """Set the details for this wire cutter."""

        self.details = details
    
    def set_max_wire_gauge_awg(self, max_wire_gauge_awg: int):
        """Set the max wire gauge for this wire cutter."""

        self.max_wire_gauge_awg = max_wire_gauge_awg
    
    def save(self):
        """Saves the wire cutter to the database along with any options."""
        
        for option in self.options:
            option.save()
        self.id = self.database_connection.save_wire_cutter(self.__dict__)


@dataclass
class SalesOrderItem:
    """Represents a sales order item."""

    database_connection: CutListDatabase
    product: Product
    due_date: datetime.datetime
    qty_to_fulfill: float
    qty_picked: float
    qty_fulfilled: float
    line_number: int
    id: int = None
    sales_order_id: int = None

    @classmethod
    def from_dict(cls, database_connection: CutListDatabase, sales_order_item_dict: dict) -> 'SalesOrderItem':
        """Creates a sales order item from a dictionary."""
        cls(database_connection, **sales_order_item_dict)

        product = Product.from_number()

        sales_order_item = cls(database_connection, )
        
        return sales_order_item
    
    @classmethod
    def find_by_product_number_and_line_number(cls, database_connection: CutListDatabase, product_number, line_number) -> 'SalesOrderItem':
        """Finds a sales order item by product number and line number. Returns None if not found."""

        items = database_connection.get_sales_order_items_by_sales_order_number()

    @classmethod
    def from_sales_order_item_id(cls, database_connection: CutListDatabase, sales_order_item_id: int) -> 'SalesOrderItem':
        """Returns a sales order item from the database by its ID."""

        return cls(database_connection, **database_connection.get_sales_order_item_by_id(sales_order_item_id))
    
    @classmethod
    def from_sales_order_id(cls, database_connection: CutListDatabase, sales_order_id: int) -> 'SalesOrderItem':
        """Returns all sales order items from the database by its sales order ID.
            Returns a list of all the items in the sales order, or an empty list if the sales order doesn't exist."""
        to_return = []

        items = database_connection.get_sales_order_items_by_sales_order_id(sales_order_id)
        for item in items:
            to_return.append(cls(database_connection, **item))
        
        return to_return

    @property
    def quantity_requseted(self) -> float:
        """Returns the quantity requested for this item."""

        return self.qty_to_fulfill - self.qty_picked - self.qty_fulfilled
    
    def save(self):
        """Saves the sales order item to the database."""

        self.id = self.database_connection.save_sales_order_item(self)
    
    def delete(self):
        """Delete the sales order item."""

        self.database_connection.delete_sales_order_item(self)
        self.id = None


@dataclass
class SalesOrder:
    """Represents a sales order."""

    database_connection: CutListDatabase
    customer_name: str
    number: str
    order_items: List[SalesOrderItem] = None
    id: int = None

    def __post_init__(self):
        """Initialize the sales order after it's been created."""

        if self.order_items is None:
            self.order_items = []

    @classmethod
    def from_dict(cls, database_connection: CutListDatabase, sales_order_dict: dict) -> 'SalesOrder':
        """Creates a sales order from a dictionary. This does not include the order items."""
        
        return cls(database_connection, **sales_order_dict)

    @classmethod
    def find_by_number(cls, database_connection: CutListDatabase, number: str) -> 'SalesOrder':
        """Returns a sales order from the database by its number. Along with the order items.
            Returns None if the sales order doesn't exist."""

        data = database_connection.get_sales_order_by_number(number)
        if not data:
            return None

        sales_order = cls(database_connection, **data)

        # Add the order items
        for item in database_connection.get_sales_order_items_by_sales_order_id(sales_order.id):
            sales_order.add_item(SalesOrderItem.from_dict(database_connection, item))

        return sales_order

    def add_item(self, item: SalesOrderItem):
        """Add a sales order item to this sales order."""
        
        self.order_items.append(item)
    
    def remove_item(self, order_item: SalesOrderItem):
        """Removes a sales order item from this sales order."""

        for item in self.order_items:
            if item != order_item:
                continue
            
            self.order_items.remove(order_item)
            item.delete()
    
    def remove_all_items(self):
        """Removes all sales order items."""

        for item in self.order_items:
            self.order_items.remove(item)
            item.delete()
    
    def save(self):
        """Saves the sales order to the database."""

        for item in self.order_items:
            item.save()
        self.id = self.database_connection.save_sales_order(self)


@dataclass
class CutJob:
    """Represents a cut job."""

    database_connection: CutListDatabase
    product: Product
    related_sales_order_item: Optional[SalesOrderItem] = None
    assigned_cutter: WireCutter = None
    quantity_cut: Optional[int] = None
    date_cut_start: Optional[datetime.datetime] = None
    date_cut_end: Optional[datetime.datetime] = None
    date_termination_start: Optional[datetime.datetime] = None
    date_termination_end: Optional[datetime.datetime] = None
    date_splice_start: Optional[datetime.datetime] = None
    date_splice_end: Optional[datetime.datetime] = None
    is_cut: bool = False
    is_spliced: bool = False
    is_terminated: bool = False
    is_ready_for_build: bool = False
    id: int = None

    @classmethod
    def from_dict(cls, database_connection: CutListDatabase, cut_job_dict: dict) -> 'CutJob':
        """Creates a cut job from a dictionary."""
        
        return cls(database_connection, **cut_job_dict)

    def set_assigned_cutter(self, cutter: WireCutter):
        """Set the assigned cutter for this cut job."""

        self.assigned_cutter = cutter
    
    def set_related_sales_order_item(self, item: SalesOrderItem):
        """Set the related sales order item for this cut job."""

        self.related_sales_order_item = item
    
    def save(self):
        """Saves the cut job to the database."""

        self.id = self.database_connection.save_cut_job(self.__dict__)
        if self.assigned_cutter != None:
            self.assigned_cutter.save()
        if self.related_sales_order_item != None:
            self.related_sales_order_item.save()

def main():
    """For testing purposes."""
    auth = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "cutlist",
            "password": "Letmein2021",
            "database": "cutlistgenerator_refactor"
        }

    database_connection = MySQLDatabaseConnection(auth)

    new_product = Product(database_connection=database_connection, number="1", description="Test Product", uom="ea", unit_price_dollars=1.0)

    print(new_product.__dict__)
    new_product.save()


if __name__ == '__main__':
    main()
import datetime
from dataclasses import dataclass
from typing import List

from cutlistgenerator.error import ProductNotInKitException
from cutlistgenerator.database.cutlistdatabase import CutListDatabase


@dataclass
class Product:
    """Represents a product."""

    database_connection: CutListDatabase
    number: str
    description: str
    uom: str
    unit_price_dollars: float = None
    kit_flag: bool = False
    parent_kit_product: 'Product' = None
    id: int = None

    def __post_init__(self):
        """Initialize the product after it's been created."""
        
        if self.kit_flag and self.parent_kit_product is None:
            raise ProductNotInKitException("Product is marked as a kit but does not have a parent kit product.")

        if self.unit_price_dollars is None:
            self.unit_price_dollars = 0.0

    @staticmethod
    def find_parent_kit_product_from_child_product_data(database_connection, product_data: dict) -> dict:
        """Finds the parent kit product from the child product data. Returns product data with 'parent_kit_product' key populated."""

        parent_kit_product = None
        parent_kit_product_data = database_connection.get_parent_product_from_child_product_id(product_data['id'])
        if parent_kit_product_data:
            parent_kit_product = Product.from_number(database_connection, parent_kit_product_data['number'])
        
        product_data['parent_kit_product'] = parent_kit_product
        return product_data

    @classmethod
    def from_number(cls, database_connection: CutListDatabase, number: str) -> 'Product':
        """Returns a product from the database by its number. Returns None if not found."""

        data = database_connection.get_product_by_number(number)
        if not data:
            return None
        
        data = cls.find_parent_kit_product_from_child_product_data(database_connection, data)

        return cls(database_connection, **data)
    
    @classmethod
    def from_id(cls, database_connection: CutListDatabase, id: int) -> 'Product':
        """Returns a product from the database by its ID. Returns None if not found."""

        data = database_connection.get_product_by_id(id)
        if not data:
            return None
        
        data = cls.find_parent_kit_product_from_child_product_data(database_connection, data)

        return cls(database_connection, **data)
    
    def set_parent_kit_product(self, parent_kit_product: 'Product'):
        """Sets the parent kit product number for this product."""

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
    description: str = None
    id: int = None

    @classmethod
    def from_number(cls, database_connection: CutListDatabase, name: str) -> 'WireCutterOption':
        """Returns a wire cutter option from the database by its name."""

        return cls(database_connection, **database_connection.get_wire_cutter_option_by_name(name))

    def save(self):
        """Saves the wire cutter option to the database."""

        self.id = self.database_connection.save_wire_cutter_option(self)


@dataclass
class WireCutter:
    """Represents a wire cutter."""

    database_connection: CutListDatabase
    name: str
    max_wire_gauge_awg: int
    processing_speed_feet_per_minute: int = None
    details: str = None
    options: List[WireCutterOption] = None
    id: int = None

    def __post_init__(self):
        """Initialize the wire cutter after it's been created."""

        if self.options is None:
            self.options = []

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
        self.id = self.database_connection.save_wire_cutter(self)


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
    def find_by_number(cls, database_connection: CutListDatabase, number: str) -> 'SalesOrder':
        """Returns a sales order from the database by its number. Along with the order items.
            Returns None if the sales order doesn't exist."""

        data = database_connection.get_sales_order_by_number(number)
        if not data:
            return None

        sales_order = cls(database_connection, **data)

        # Add the order items
        for item in database_connection.get_sales_order_items_by_sales_order_id(sales_order.id):
            # id, sales_order_id, qty_to_fulfill, line_number, qty_picked, qty_fulfilled, due_date

            product = Product.from_id(database_connection, id=item['product_id'])

            order_item = SalesOrderItem(database_connection,
                                        product,
                                        due_date=item['due_date'],
                                        qty_to_fulfill=item['qty_to_fulfill'],
                                        qty_picked=item['qty_picked'],
                                        qty_fulfilled=item['qty_fulfilled'],
                                        line_number=item['line_number'],
                                        sales_order_id=item['sales_order_id'])

            sales_order.add_item(order_item)

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
    related_sales_order_item: SalesOrderItem = None
    assigned_wire_cutter: WireCutter = None
    quantity_cut: int = None
    date_cut_start: datetime.datetime = None
    date_cut_end: datetime.datetime = None
    date_termination_start: datetime.datetime = None
    date_termination_end: datetime.datetime = None
    date_splice_start: datetime.datetime = None
    date_splice_end: datetime.datetime = None
    is_cut: bool = False
    is_spliced: bool = False
    is_terminated: bool = False
    is_ready_for_build: bool = False
    id: int = None

    def set_assigned_wire_cutter(self, wire_cutter: WireCutter):
        """Set the assigned wire cutter for this cut job."""

        self.assigned_wire_cutter = wire_cutter
    
    def set_related_sales_order_item(self, item: SalesOrderItem):
        """Set the related sales order item for this cut job."""

        self.related_sales_order_item = item
    
    def save(self):
        """Saves the cut job to the database."""

        self.id = self.database_connection.save_cut_job(self)
        if self.assigned_wire_cutter != None:
            self.assigned_wire_cutter.save()
        if self.related_sales_order_item != None:
            self.related_sales_order_item.save()
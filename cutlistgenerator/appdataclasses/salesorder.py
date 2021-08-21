from . import datetime, dataclass, List
from . import CutListDatabase
from .product import Product


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
    cut_in_full: bool = False
    date_added: datetime.datetime = None
    
    @classmethod
    def find_by_product_number_and_line_number(cls, database_connection: CutListDatabase, product_number, line_number) -> 'SalesOrderItem':
        """Finds a sales order item by product number and line number. Returns None if not found."""
        raise NotImplementedError()
        items = database_connection.get_sales_order_items_by_sales_order_number()

    @classmethod
    def from_id(cls, database_connection: CutListDatabase, sales_order_item_id: int) -> 'SalesOrderItem':
        """Returns a sales order item from the database by its ID. Returns None if not found."""

        data = database_connection.get_sales_order_item_by_id(sales_order_item_id)
        if not data:
            return None
        product = Product.from_id(database_connection, data['product_id'])
        del data['product_id']
        data['product'] = product
        return cls(database_connection, **data)
    
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
    def quantity_left_to_ship(self) -> float:
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
    def from_sales_order_item_id(cls, database_connection: CutListDatabase, sales_order_item_id: int) -> 'SalesOrder':
        """Returns a sales order from the database by one of its items ID. Returns None if not found."""
        data = database_connection.get_sales_order_by_sales_order_item_id(sales_order_item_id)
        if not data:
            return None
        sales_order = cls(database_connection, **data['sales_order'])

        for sales_order_item_data in data['sales_order_items']:
            product = Product.from_id(database_connection, sales_order_item_data['product_id'])

            # Remove unneeded data
            del sales_order_item_data['product_id']

            sales_order_item = SalesOrderItem(database_connection, product, **sales_order_item_data)
            sales_order.add_item(sales_order_item)

        return sales_order

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
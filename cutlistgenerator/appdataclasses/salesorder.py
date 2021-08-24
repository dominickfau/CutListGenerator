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
    date_added: datetime.datetime = None
    
    @classmethod
    def find_by_product_and_line_number(cls, database_connection: CutListDatabase, product: Product, line_number: str) -> List['SalesOrderItem']:
        """Finds a sales order item by product and line number. Returns empty list if not found."""
        sales_order_items = []
        data = database_connection.get_sales_order_item_by_product_and_line_number(product, line_number)
        if not data:
            return []
        
        for row in data:
            product_data = {
                'id': data['product_id'],
                'number': data['product_name'],
                'description': data['product_description'],
                'uom': data['product_uom'],
                'unit_price_dollars': data['product_unit_price_dollars'],
                'kit_flag': data['kit_flag'],
                'parent_kit_product': Product.from_id(database_connection, data['parent_kit_product_id'])
            }
            product = Product(database_connection, **product_data)
            
            sales_order_item_data = {
                'id': data['id'],
                'product': product,
                'due_date': data['due_date'],
                'qty_to_fulfill': data['qty_to_fulfill'],
                'qty_picked': data['qty_picked'],
                'qty_fulfilled': data['qty_fulfilled'],
                'line_number': data['line_number'],
                'sales_order_id': data['so_id']
            }
            sales_order_item = SalesOrderItem(database_connection, **sales_order_item_data)
            sales_order_items.append(sales_order_item)
        return sales_order_items

    @classmethod
    def from_id(cls, database_connection: CutListDatabase, sales_order_item_id: int) -> 'SalesOrderItem':
        """Returns a sales order item from the database by its ID. Returns None if not found."""

        data = database_connection.get_sales_order_item_by_id(sales_order_item_id)
        _ = data.pop("cut_in_full", None)
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
            _ = item.pop("cut_in_full", None)
            to_return.append(cls(database_connection, **item))
        
        return to_return

    @property
    def quantity_left_to_ship(self) -> float:
        """Returns the quantity requested for this item."""

        return self.qty_to_fulfill - self.qty_picked - self.qty_fulfilled
    
    @property
    def cut_in_full(self) -> bool:
        """Returns true if the item is fully cut."""
        # TODO: Check that this works as intended.
        cut_jobs = []
        data = self.database_connection.get_cut_jobs_by_so_item_id(self.id)
        total_qty_cut = 0
        for cut_job in data:
            if not cut_job['is_cut']:
                continue
            total_qty_cut += cut_job['quantity_cut']
        return total_qty_cut >= self.quantity_left_to_ship
    
    @property
    def cut_in_full_as_string(self) -> str:
        """Returns a string indicating whether the item is fully cut."""
        if self.cut_in_full:
            return "Yes"
        return "No"
    
    @property
    def qty_left_to_cut(self) -> float:
        """Returns total quantity left to cut."""
        # TODO: Check that this works as intended.
        cut_jobs = []
        data = self.database_connection.get_cut_jobs_by_so_item_id(self.id)
        total_qty_cut = 0
        for cut_job in data:
            if not cut_job['is_cut']:
                continue
            total_qty_cut += cut_job['quantity_cut']
        return self.quantity_left_to_ship - total_qty_cut
    
    @property
    def qty_scheduled_to_cut(self) -> float:
        """Returns the quantity scheduled to be cut."""
        # TODO: Check that this works as intended.
        cut_jobs = []
        data = self.database_connection.get_cut_jobs_by_so_item_id(self.id)
        total_qty_cut = 0
        for cut_job in data:
            if cut_job['is_cut']:
                continue
            total_qty_cut += cut_job['quantity_cut']
        return total_qty_cut
    
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
    
    @staticmethod
    def remove_all_sales_order_items_for_product(database_connection: CutListDatabase, product: Product) -> None:
        """Removes all sales order items for a given product."""

        data = database_connection.get_sales_orders_containing_product(product)
        for row in data:
            sales_order_id = row['sales_order_id']
            sales_order = SalesOrder.from_id(database_connection, sales_order_id)
            for item in sales_order.order_items:
                if item.product.id != product.id:
                    continue
                sales_order.remove_item(item)
            sales_order.save()

    @classmethod
    def from_id(cls, database_connection: CutListDatabase, sales_order_id: int) -> 'SalesOrder':
        """Returns a sales order from the database by its ID. Returns None if not found."""

        data = database_connection.get_sales_order_by_id(sales_order_id)
        if not data:
            return None

        sales_order = cls(database_connection, **data)

        # Add the order items
        for item in database_connection.get_sales_order_items_by_sales_order_id(sales_order.id):
            # id, sales_order_id, qty_to_fulfill, line_number, qty_picked, qty_fulfilled, due_date

            product = Product.from_id(database_connection, id=item['product_id'])

            order_item = SalesOrderItem.from_id(database_connection, sales_order_item_id=item['id'])

            sales_order.add_item(order_item)

        return sales_order

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
            del sales_order_item_data['cut_in_full']

            sales_order_item = SalesOrderItem(database_connection, product, **sales_order_item_data)
            sales_order.add_item(sales_order_item)

        return sales_order
    
    @classmethod
    def get_number_from_sales_order_item_id(cls, database_connection: CutListDatabase, sales_order_item_id: int) -> str:
        """Returns the sales order number from a sales order item ID."""

        data = database_connection.get_sales_order_by_sales_order_item_id(sales_order_item_id)
        if not data:
            return None
        return data['sales_order']['number']

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

            order_item = SalesOrderItem.from_id(database_connection, sales_order_item_id=item['id'])

            sales_order.add_item(order_item)

        return sales_order

    def add_item(self, item: SalesOrderItem):
        """Add a sales order item to this sales order."""
        if item in self.order_items:
            return
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
    
    def save(self, skip_items: bool = False):
        """Saves the sales order to the database."""

        self.id = self.database_connection.save_sales_order(self)
        for item in self.order_items:
            item.sales_order_id = self.id
            if skip_items is False:
                item.save()
    
    def delete(self):
        """Delete the sales order."""
        for item in self.order_items:
            item.delete()
        
        self.database_connection.delete_sales_order(self)
        self.id = None
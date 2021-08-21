from typing import Optional, List
from . import datetime, dataclass
from . import CutListDatabase
from .product import Product
from .wirecutter import WireCutter
from .salesorder import SalesOrderItem


@dataclass
class CutJob:
    """Represents a cut job."""

    database_connection: CutListDatabase
    product: Product
    assigned_wire_cutter: WireCutter
    related_sales_order_item: SalesOrderItem = None
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
    date_created: datetime.datetime = None

    def __post_init__(self):
        if self.date_created == None:
            self.date_created = datetime.datetime.now()
        
    @classmethod
    def from_id(cls, database_connection: CutListDatabase, id: int):
        """Loads the cut job from the database by its ID."""
        cut_job_data = database_connection.get_cut_job_by_id(id)
        if not cut_job_data:
            return None
        
        product_id = cut_job_data.pop('product_id')
        wire_cutter_id = cut_job_data.pop('assigned_wire_cutter_id')
        sales_order_item_id = cut_job_data.pop('related_sales_order_item_id')
        product = Product.from_id(database_connection, product_id)
        wire_cutter = WireCutter.from_id(database_connection, wire_cutter_id)
        sales_order_item = None
        if sales_order_item_id != None:
            sales_order_item = SalesOrderItem.from_id(database_connection, sales_order_item_id)
        cut_job = cls(database_connection, product, wire_cutter, sales_order_item, **cut_job_data)
        return cut_job

    @classmethod
    def from_sales_order_item_id(cls, database_connection: CutListDatabase, sales_order_item_id: int) -> 'CutJob':
        """Loads a cut job from the database given the sales order item id. Returns None if no cut job was found."""
        # TODO: Handle cases of multiple cut jobs for the same sales order item.
        data = database_connection.get_cut_job_by_so_item_id(sales_order_item_id)
        if not data:
            return None
        product_id = data[0].pop('product_id')
        product = Product.from_id(database_connection, product_id)
        wire_cutter_id = data[0].pop('assigned_wire_cutter_id')
        wire_cutter = WireCutter.from_id(database_connection, wire_cutter_id)
        sales_order_item_id = data[0].pop('related_sales_order_item_id')
        related_sales_order_item = SalesOrderItem.from_id(database_connection, sales_order_item_id)
        
        cut_job = cls(database_connection, product, wire_cutter, related_sales_order_item, **data[0])
        return cut_job
    
    @classmethod
    def get_all_open(cls, database_connection: CutListDatabase) -> List['CutJob']:
        """Returns all open cut jobs."""
        data = database_connection.get_all_open_cut_jobs()
        if not data:
            return []
        
        cut_jobs = []
        for cut_job_data in data:
            product_id = cut_job_data.pop('product_id')
            product = Product.from_id(database_connection, product_id)
            wire_cutter_id = cut_job_data.pop('assigned_wire_cutter_id')
            wire_cutter = WireCutter.from_id(database_connection, wire_cutter_id)
            sales_order_item_id = cut_job_data.pop('related_sales_order_item_id')
            related_sales_order_item = SalesOrderItem.from_id(database_connection, sales_order_item_id)
            cut_job = cls(database_connection, product, wire_cutter, related_sales_order_item, **cut_job_data)
            cut_jobs.append(cut_job)
        return cut_jobs

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
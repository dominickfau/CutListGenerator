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
    
    @property
    def is_ready_for_build_as_string(self):
        """Returns a string indicating if the cut job is ready for build."""
        if self.is_ready_for_build:
            return "Yes"
        return "No"
    
    @property
    def is_cut_as_string(self):
        """Returns a string indicating if the cut job is cut."""
        if self.is_cut:
            return "Yes"
        return "No"
    
    @property
    def is_terminated_as_string(self):
        """Returns a string indicating if the cut job is terminated."""
        if self.is_terminated:
            return "Yes"
        return "No"
    
    @property
    def is_spliced_as_string(self):
        """Returns a string indicating if the cut job is spliced."""
        if self.is_spliced:
            return "Yes"
        return "No"
        
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
    def from_sales_order_item_id(cls, database_connection: CutListDatabase, sales_order_item_id: int) -> List['CutJob']:
        """Returns all cut jobs from the database for the given sales order item id. Returns empty list if no cut job was found."""
        cut_jobs = []
        data = database_connection.get_cut_jobs_by_so_item_id(sales_order_item_id)
        if not data:
            return []
        for item in data:
            product_id = item.pop('product_id')
            product = Product.from_id(database_connection, product_id)
            wire_cutter_id = item.pop('assigned_wire_cutter_id')
            wire_cutter = WireCutter.from_id(database_connection, wire_cutter_id)
            sales_order_item_id = item.pop('related_sales_order_item_id')
            related_sales_order_item = SalesOrderItem.from_id(database_connection, sales_order_item_id)
            cut_job = cls(database_connection, product, wire_cutter, related_sales_order_item, **item)
            cut_jobs.append(cut_job)
        return cut_jobs
    
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
            related_sales_order_item = None
            if sales_order_item_id != None:
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
        if self.date_cut_end:
            self.is_cut = True

        if self.date_termination_end:
            self.is_terminated = True

        if self.date_splice_end:
            self.is_spliced = True
        
        if self.is_cut and self.is_terminated and self.is_spliced:
            self.is_ready_for_build = True

        self.id = self.database_connection.save_cut_job(self)
        if self.assigned_wire_cutter != None:
            self.assigned_wire_cutter.save()
        if self.related_sales_order_item != None:
            self.related_sales_order_item.save()
from typing import Optional
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
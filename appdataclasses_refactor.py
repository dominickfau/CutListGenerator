import datetime
from dataclasses import dataclass
from typing import Optional, List


class Auditing:
    """Base class for adding audit information to a class."""
    
    def __init__(self):
        self.date_created = datetime.datetime.now()
        self.date_modified = datetime.datetime.now()
    
    def update_date_modified(self):
        """Update the date_modified attribute to the current date/time."""

        self.date_modified = datetime.datetime.now()


@dataclass
class WireCutterOption:
    """Represents a wire cutter option."""

    name: str
    description: Optional[str] = None
    id: Optional[int] = None
    
    @classmethod
    def from_database(cls, db_entry: dict):
        """Creates a new wire cutter option from a database entry."""

        return cls(name=db_entry["name"], description=db_entry["description"], id=db_entry["id"])


@dataclass
class WireCutter(Auditing):
    """Represents a wire cutter."""

    name: str
    max_wire_gauge_awg: int
    details: Optional[str] = None
    options: Optional[List[WireCutterOption]] = None
    id: Optional[int] = None

    def __post_init__(self):
        """Initialize the wire cutter after it's been created."""

        super().__init__()
        if self.options is None:
            self.options = []

    def add_option(self, option: WireCutterOption):
        """Add a wire cutter option to this wire cutter. If the option already exists, it will be updated."""

        self.date_modified = datetime.datetime.now()
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

        self.update_date_modified()
        if option in self.options:
            self.options.remove(option)
    
    def set_details(self, details: str):
        """Set the details for this wire cutter."""

        self.update_date_modified()
        self.details = details
    
    def set_max_wire_gauge_awg(self, max_wire_gauge_awg: int):
        """Set the max wire gauge for this wire cutter."""

        self.update_date_modified()
        self.max_wire_gauge_awg = max_wire_gauge_awg
    
    @classmethod
    def from_database(cls, db_entry: dict, options: List[WireCutterOption] = None):
        """Creates a new wire cutter from a database entry."""

        wire_cutter = cls(
            name=db_entry["name"],
            max_wire_gauge_awg=db_entry["max_wire_gauge_awg"],
            details=db_entry["details"],
            id=db_entry["id"]
        )

        if options != None:
            wire_cutter.options = options
        
        wire_cutter.date_created = db_entry["date_created"]
        wire_cutter.date_modified = db_entry["date_modified"]

        return wire_cutter


@dataclass
class Product:
    """Represents a product."""

    number: str
    description: str
    uom: str
    unit_price_dollars: Optional[float] = None
    kit_flag: bool = False
    parent_kit_product_number: Optional[str] = None
    id: Optional[int] = None

    @classmethod
    def from_database(cls, db_entry: dict):
        """Creates a new product from a database entry."""

        return cls(
            number=db_entry["number"],
            description=db_entry["description"],
            uom=db_entry["uom"],
            unit_price_dollars=db_entry["unit_price_dollars"],
            kit_flag=db_entry["kit_flag"],
            parent_kit_product_number=db_entry["parent_kit_product_number"],
            id=db_entry["id"]
        )



@dataclass
class CutJob(Auditing):
    """Represents a cut job."""

    customer_name: str
    sales_order_number: str
    due_date: datetime.datetime
    product: Product
    quantity_requseted: int
    line_number: int
    assigned_cutter: Optional[WireCutter] = None
    on_cut_list: bool = False
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
    id: Optional[int] = None

    def __post_init__(self):
        """Initialize the cut job after it's been created."""
        
        super().__init__()
    
    def set_assigned_cutter(self, cutter: WireCutter):
        """Set the assigned cutter for this cut job."""

        self.update_date_modified()
        self.assigned_cutter = cutter

    @classmethod
    def from_database(cls, db_entry: dict, product: Product, assigned_cutter: WireCutter = None):
        """Creates a new cut job from a database entry."""

        cut_job = cls(
            customer_name=db_entry["customer_name"],
            sales_order_number=db_entry["sales_order_number"],
            due_date=db_entry["due_date"],
            product=product,
            quantity_requested=db_entry["quantity_requested"],
            line_number=db_entry["line_number"],
            on_cut_list=db_entry["on_cut_list"],
            quantity_cut=db_entry["quantity_cut"],
            date_cut_start=db_entry["date_cut_start"],
            date_cut_end=db_entry["date_cut_end"],
            date_termination_start=db_entry["date_termination_start"],
            date_termination_end=db_entry["date_termination_end"],
            date_splice_start=db_entry["date_splice_start"],
            date_splice_end=db_entry["date_splice_end"],
            is_cut=db_entry["is_cut"],
            is_spliced=db_entry["is_spliced"],
            is_terminated=db_entry["is_terminated"],
            is_ready_for_build=db_entry["is_ready_for_build"],
            id=db_entry["id"]
        )

        if assigned_cutter != None:
            cut_job.set_assigned_cutter(assigned_cutter)

        cut_job.date_created = db_entry["date_created"]
        cut_job.date_modified = db_entry["date_modified"]

        return cut_job





def main():
    """Used for testing this module."""

    hot_stamp_option = WireCutterOption(name="Hot Stamping", id=1)
    termination_option = WireCutterOption(name="Auto Termination", id=2)
    wire_twisting_option = WireCutterOption(name="Wire Twisting", id=3)
    seal_insertion_option = WireCutterOption(name="Seal Insertion", id=4)

    kappa_330 = WireCutter(name="Kappa 330",
                        max_wire_gauge_awg=0
                        )

    kappa_330.add_option(hot_stamp_option)
    kappa_330.add_option(termination_option)
    kappa_330.add_option(wire_twisting_option)
    kappa_330.add_option(seal_insertion_option)

    print(kappa_330)


if __name__ == '__main__':
    main()
import datetime
from dataclasses import dataclass
from typing import Optional, List


class Auditing:
    """Base class for adding audit information to a class."""
    
    def __init__(self):
        self.date_created = datetime.datetime.now()
        self.date_modified = datetime.datetime.now()
    
    def update_date_modified(self):
        """Update the date_modified attribute."""

        self.date_modified = datetime.datetime.now()


@dataclass
class WireCutterOption:
    """Represents a wire cutter option."""

    name: str
    description: Optional[str] = None
    id: Optional[int] = None
    
    @classmethod
    def from_database(cls, db_entry: dict):
        """Create a new wire cutter from a database wire cutter."""

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
        """Create a new wire cutter from a database entry."""

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
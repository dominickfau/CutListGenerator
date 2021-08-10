from . import dataclass, List
from . import CutListDatabase


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
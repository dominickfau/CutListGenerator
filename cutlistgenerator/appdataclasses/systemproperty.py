from . import datetime, dataclass, CutListDatabase


@dataclass
class SystemProperty:
    """Represents a system property."""

    database_connection: CutListDatabase
    system_key: str
    system_value: str
    date_last_modified: datetime.datetime = None
    read_allowed: bool = False
    write_allowed: bool = False
    id: int = None

    def __post_init__(self):
        """Initialize the system property after it's been created."""

        if self.date_last_modified is None:
            self.date_last_modified = datetime.datetime.now()

    def save(self):
        """Saves the system property to the database."""

        self.id = self.database_connection.save_system_property(self)
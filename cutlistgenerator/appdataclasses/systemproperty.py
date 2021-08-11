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

    def __repr__(self) -> str:
        """Returns the representation of the system property."""
        
        return f"SystemProperty(database_connection={self.database_connection}, system_key={self.system_key}, system_value={self.system_value}, date_last_modified={self.date_last_modified}, read_allowed={self.read_allowed}, write_allowed={self.write_allowed}, id={self.id})"
    
    def __str__(self) -> str:
        """Returns the string representation of the system property."""
        return f"{self.system_key} = {self.system_value}"
    
    def set_value(self, value: str) -> None:
        """Sets the system property's value."""

        self.system_value = value
        self.date_last_modified = datetime.datetime.now()
        self.save()

    def save(self) -> None:
        """Saves the system property to the database."""

        self.id = self.database_connection.save_system_property(self)

    def delete(self):
        """Deletes the system property from the database."""

        self.database_connection.delete_system_property(self)




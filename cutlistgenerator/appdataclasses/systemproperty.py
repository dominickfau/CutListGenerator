from . import datetime, dataclass, CutListDatabase


@dataclass
class SystemProperty:
    """Represents a system property. Defaults to not visible and not read only."""

    database_connection: CutListDatabase
    name: str
    value: str
    date_last_modified: datetime.datetime = None
    read_only: bool = False
    visible: bool = False
    id: int = None

    def __post_init__(self):
        """Initialize the system property after it's been created."""

        if self.date_last_modified is None:
            self.date_last_modified = datetime.datetime.now()
        

    def __repr__(self) -> str:
        """Returns the representation of the system property."""
        
        return f"SystemProperty(database_connection={self.database_connection}, name={self.name}, value={self.value}, date_last_modified={self.date_last_modified}, read_only={self.read_only}, visible={self.visible}, id={self.id})"
    
    def __str__(self) -> str:
        """Returns the string representation of the system property."""
        return f"{self.name} = {self.value}"
    
    @classmethod
    def find_by_name(cls, database_connection: CutListDatabase, name: str) -> 'SystemProperty':
        """Finds a system property by its name. Returns None if the system property is not found."""
        data = database_connection.get_system_property_by_name(name)
        if not data:
            return None
        return SystemProperty(database_connection=database_connection, **data)
    
    def set_value(self, value: str) -> None:
        """Sets the system property's value."""

        self.value = value
        self.date_last_modified = datetime.datetime.now()
        self.save()
    
    def set_read_only(self, read_only: bool) -> None:
        """Sets the system property's read only status for the end user."""

        self.read_only = read_only
        self.save()
    
    def set_visible(self, visible: bool) -> None:
        """Sets the system property's visibility to the end user."""
        
        self.visible = visible
        self.save()

    def save(self) -> None:
        """Saves the system property to the database."""

        self.id = self.database_connection.save_system_property(self)

    def delete(self):
        """Deletes the system property from the database."""

        self.database_connection.delete_system_property(self)




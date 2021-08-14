import mysql.connector
from abc import abstractmethod
from typing import List


class Database:
    """Base class for Databases"""

    def __init__(self, connection_args: dict):
        """Initialize the Database"""

        self.connection = None
        self.connection_args = connection_args
    
    @abstractmethod
    def create(self, force_remove_old_data: bool = False) -> None:
        """Create the Database"""
        pass

    @abstractmethod
    def connect(self):
        """Connect to database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from database."""
        pass

    @abstractmethod
    def get_current_version(self):
        """Get the current version of the database."""
        pass
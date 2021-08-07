import json
import os

from cutlistgenerator.error import InvalidSettingsFilePathException

DEFULT_SETTINGS = {
    "Fishbowl_MySQL":
    {
        "auth": {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "gone",
            "password": "fishing",
            "database": "qes"
        }
    },
    "CutList_MySQL":
    {
        "auth": {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "cutlist",
            "password": "Letmein2021",
            "database": "cutlistgenerator"
        }
    }
}

class Settings:
    """Settings class."""

    def __init__(self):
        """Initialize. Loads default settings."""

        self.file_path = None
        self.fishbowl_settings = DEFULT_SETTINGS["Fishbowl_MySQL"]
        self.cutlist_settings = DEFULT_SETTINGS["CutList_MySQL"]
        self.load()
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate file path."""

        return os.path.isfile(file_path)

    def get_fishbowl_settings(self) -> dict:
        """Get fishbowl settings."""

        return self.fishbowl_settings
    
    def get_cutlist_settings(self) -> dict:
        """Get cutlist settings."""
        
        return self.cutlist_settings
    
    def set_file_path(self, file_path: str) -> None:
        """Set file path."""

        if not Settings.validate_file_path(file_path):
            raise InvalidSettingsFilePathException(f"Could not set file path: {file_path}.", file_path=file_path)
        
        self.file_path = file_path
    
    def load(self) -> None:
        """Load settings from file."""

        if not self.file_path:
            self.fishbowl_settings = DEFULT_SETTINGS["Fishbowl_MySQL"]
            self.cutlist_settings = DEFULT_SETTINGS["CutList_MySQL"]
            return

        if not self.validate_file_path(self.file_path):
            raise InvalidSettingsFilePathException(f"Could not load settings from file: {self.file_path}.", file_path=self.file_path)
        
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        
        self.fishbowl_settings = data["Fishbowl_MySQL"]
        self.cutlist_settings = data["CutList_MySQL"]

    def save_to_file_path(self, file_path: str) -> None:
        """Save settings to file to disk. This also updates the file path."""

        if not self.validate_file_path(self.file_path):
            raise InvalidSettingsFilePathException(f"Could not load settings from file: {self.file_path}.", file_path=self.file_path)
        
        self.file_path = file_path
        
        data = {
            "Fishbowl_MySQL": self.fishbowl_settings,
            "CutList_MySQL": self.cutlist_settings
        }

        with open(file_path, 'w') as file:
            json.dumps(data, file, indent=4)
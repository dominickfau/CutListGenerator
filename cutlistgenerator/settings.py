import json
import os

from .error import InvalidSettingsFilePathError, InvalidSettingsFileError

DEFULT_SETTINGS = {
    "General_Settings": {
        "logging_level": "DEBUG",
        "database_setup": False
    },
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

    def __init__(self, file_path: os.PathLike = None):
        """Initialize. Loads default settings."""
        self._file_path = file_path
        self.load()
    
    def __dict__(self) -> dict:
        """Return dictionary representation of settings."""

        return {
            "General_Settings": self._generate_settings,
            "Fishbowl_MySQL": self._fishbowl_settings,
            "CutList_MySQL": self._cutlist_settings
        }
    
    def is_database_setup(self) -> bool:
        """Check if database is setup."""
        return self._generate_settings["database_setup"]
    
    def set_database_setup(self, value: bool) -> None:
        """Set database setup."""
        self._generate_settings["database_setup"] = value
        self.save()
    
    def get_logging_level(self) -> str:
        """Get logging level."""
        return self._generate_settings["logging_level"]
    
    def load_default_settings(self) -> None:
        """Loads default settings."""
        self._fishbowl_settings = DEFULT_SETTINGS["Fishbowl_MySQL"]
        self._cutlist_settings = DEFULT_SETTINGS["CutList_MySQL"]
        self._generate_settings = DEFULT_SETTINGS["General_Settings"]
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate file path."""
        return os.path.isfile(file_path)
    
    @staticmethod
    def validate_file_extention(file_path: str) -> bool:
        """Validate file extention. Returns True if the file extention is .json."""
        return file_path.endswith(".json")
        
    def get_fishbowl_settings(self) -> dict:
        """Get fishbowl settings."""
        return self._fishbowl_settings
    
    def get_cutlist_settings(self) -> dict:
        """Get cutlist settings."""
        return self._cutlist_settings
    
    def set_file_path(self, file_path: str) -> None:
        """Set file path."""
        if not Settings.validate_file_path(file_path):
            raise InvalidSettingsFilePathError(f"Could not set file path: {file_path}.", file_path=file_path)
        
        if not Settings.validate_file_extention(file_path):
            raise InvalidSettingsFileError(message=f"File extention: {file_path.split('.')[-1]} is not a valid file extention.", file_path=file_path)
        
        self._file_path = file_path
    
    def load(self) -> None:
        """Load settings from file."""

        if not self._file_path:
            self.load_default_settings()
            return

        if not Settings.validate_file_path(self._file_path):
            raise InvalidSettingsFilePathError(f"Could not load settings from file: {self._file_path}.", file_path=self._file_path)
        
        try:
            with open(self._file_path, 'r') as file:
                data = json.loads(file.read())
        except json.JSONDecodeError:
            raise InvalidSettingsFileError(message=f"Error while loading settings from file: {self._file_path}. Check that the file is valid JSON.",
                                            file_path=self._file_path)
        
        self._fishbowl_settings = data["Fishbowl_MySQL"]
        self._cutlist_settings = data["CutList_MySQL"]
        self._generate_settings = data["General_Settings"]
    
    def save(self) -> None:
        """Save settings to file to disk."""

        with open(self._file_path, 'w') as file:
            file.write(json.dumps(self.__dict__(), indent=4))

    def save_to_file_path(self, file_path: str) -> None:
        """Save settings to file to disk. This also updates the file path."""

        if not self.validate_file_path(self._file_path):
            raise InvalidSettingsFilePathError(f"Could not load settings from file: {self._file_path}.", file_path=self._file_path)
        
        self._file_path = file_path
        
        self.save()
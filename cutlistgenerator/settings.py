import json
import os

from cutlistgenerator.error import InvalidSettingsFilePathError, InvalidSettingsFileError

DEFULT_SETTINGS = {
    "General_Settings": {
        "logging_level": "INFO"
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

    def __init__(self):
        """Initialize. Loads default settings."""

        self._file_path = None
        self.load()
    
    def __dict__(self) -> dict:
        """Return dictionary representation of settings."""

        return {
            "General_Settings": self._generate_settings,
            "Fishbowl_MySQL": self._fishbowl_settings,
            "CutList_MySQL": self._cutlist_settings
        }
    
    def load_default_settings(self) -> None:
        """Loads default settings."""

        self._fishbowl_settings = DEFULT_SETTINGS["Fishbowl_MySQL"]
        self._cutlist_settings = DEFULT_SETTINGS["CutList_MySQL"]
        self._generate_settings = DEFULT_SETTINGS["General_Settings"]
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate file path."""

        return os.path.isfile(file_path)

    def get_logging_level(self) -> str:
        """Get logging level."""
        
        return self._generate_settings["logging_level"]
        
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
        
        if ".json" not in file_path:
            raise InvalidSettingsFileError("Settings file must be a JSON file.", file_path=file_path)
        
        self._file_path = file_path
    
    def load(self) -> None:
        """Load settings from file."""

        if not self._file_path:
            self.load_default_settings()
            return

        if not self.validate_file_path(self._file_path):
            raise InvalidSettingsFilePathError(f"Could not load settings from file: {self._file_path}.", file_path=self._file_path)
        
        try:
            with open(self._file_path, 'r') as file:
                data = json.loads(file.read())
        except json.JSONDecodeError:
            raise InvalidSettingsFileError(message=f"Error while loading settings from file: {self._file_path}. Check that the file is valid JSON.",
                                            file_path=self._file_path)
        
        self._fishbowl_settings = data["Fishbowl_MySQL"]
        self._cutlist_settings = data["CutList_MySQL"]
    
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
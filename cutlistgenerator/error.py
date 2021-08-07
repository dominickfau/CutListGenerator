"""All exceptions used in the cutlistgenerator package."""

class GeneralException(Exception):
    """Base class for all exceptions."""
    
    def __init__(self, message):
        super().__init__(message)


class ProductNotInKitException(GeneralException):
    """Exception raised when a product is marked as a kit but does not have a parent kit product number."""
    pass


class InvalidSettingsFilePathException(GeneralException):
    """Exception raised when the settings file path is invalid."""
    
    def __init__(self, message, file_path):
        super().__init__(message)
        self.file_path = file_path


class NoRowSelectedException(GeneralException):
    """Exception raised when no row is selected in the table."""
    pass
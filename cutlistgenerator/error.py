"""All Errors used in the cutlistgenerator package."""

class GeneralError(Exception):
    """Base class for all Errors."""
    
    def __init__(self, message):
        super().__init__(message)

class ProductNotInKitError(GeneralError):
    """Error raised when a product is marked as a kit but does not have a parent kit product number."""
    pass

class InvalidFilePathError(GeneralError):
    """General Error for invalid file paths."""
    
    def __init__(self, message, file_path):
        super().__init__(message)
        self.file_path = file_path

class InvalidSettingsFilePathError(InvalidFilePathError):
    """Error raised when the settings file path is invalid."""
    pass

class InvalidSettingsFileError(GeneralError):
    """Error raised when the settings file cannot be parsed."""
    
    def __init__(self, message, file_path):
        super().__init__(message)
        self.file_path = file_path

class NoRowSelectedError(GeneralError):
    """Error raised when no row is selected in the table."""
    pass

class UnknownTypeConversionWarning(UserWarning):
    """Warning raised when an unknown type conversion is requested."""
    
    pass
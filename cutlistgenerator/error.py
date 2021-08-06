"""All exceptions used in the cutlistgenerator package."""

class CutListGeneratorError(Exception):
    """Base class for all exceptions."""
    def __init__(self, message, error_number=None):
        super().__init__(message)
        self.error_number = error_number


class ProductNotInKitError(CutListGeneratorError):
    """Exception raised when a product is marked as a kit but does not have a parent kit product number."""
    pass

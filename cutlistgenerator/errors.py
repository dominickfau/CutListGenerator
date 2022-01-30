"""All Errors used in the cutlistgenerator package."""


class Error(Exception):
    """Base class for exceptions in the cutlistgenerator package."""

    pass


class AuthenticationError(Error):
    """Exception raised when user authentication fails."""

    pass


class UserInactiveError(Error):
    """Raised when users active flag is set to False."""

    pass


class ValidationError(Error):
    """Raised when a value is invalid."""

    pass


class DeleteError(Error):
    """Raised when an object cannot be deleted from the database."""

    pass


class DatabaseError(Error):
    """Raised when a database operation fails."""

    pass


class SaveError(DatabaseError):
    """Raised when an object cannot be saved to the database."""

    pass

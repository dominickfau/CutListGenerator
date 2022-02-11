"""All errors for FishbowlORM."""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidDatabase(Error):
    """Raised when the database is invalid."""
    pass

class InvalidHostOrPort(Error):
    """Raised when the host or port is invalid."""
    pass

class AuthenticationError(Error):
    """Raised when the authentication fails."""
    pass


class DatabaseReadOnlyError(Error):
    """Raised when the database is in read-only mode."""
    pass
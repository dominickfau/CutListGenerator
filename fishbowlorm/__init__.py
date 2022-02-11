import sqlalchemy
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from . import errors


__version__ = "1.0.1"
SUPPORTED_UP_TO_RELEASE_YEAR = 2019
SUPPORTED_UP_TO_VERSION = 12
SUPPORTED_UP_TO_VERSION_STRING = (
    f"{SUPPORTED_UP_TO_RELEASE_YEAR}.{SUPPORTED_UP_TO_VERSION}"
)

Base = declarative_base()  # type: sqlalchemy.ext.declarative.api.DeclarativeMeta

from .models.databaseversion import FBDatabaseVersion


def before_commit(*args, **kwargs):
    """This function is called before a commit is made to the database.
    It is used to force read-only mode for the database.
    """
    session = kwargs["session"]
    if session.is_active and session.is_modified():
        raise errors.DatabaseReadOnlyError("Database is in read-only mode.")


class FishbowlORM:
    def __init__(
        self,
        db_name: str,
        host: str,
        port: str = "3305",
        username: str = "gone",
        password: str = "fishing",
    ) -> None:
        self.db_name = db_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        event.listen(Session, "before_commit", before_commit)

        self.session = Session()  # type: sqlalchemy.orm.session.Session

        # Check if the connection is valid.
        try:
            self.session.execute("SELECT DATABASE()")
        except sqlalchemy.exc.OperationalError as error:
            if error.orig.args[0] == 1049:
                raise errors.InvalidDatabase(
                    f"Database '{self.db_name}' does not exist."
                ) from error
            elif error.orig.args[0] == 2003:
                raise errors.InvalidHostOrPort(
                    f"Could not connect to host '{self.host} 'on port '{self.port}'."
                ) from error
            elif error.orig.args[0] == 1045:
                raise errors.AuthenticationError(
                    f"Invalid username or password. {error.orig.args[1]}"
                ) from error
            else:
                raise error

        # # Check if the database is a valid Fishbowl database.
        # try:
        #     db_version = FBDatabaseVersion.find_current_version(self)
        #     release_year, version_number = FBDatabaseVersion.split_version(
        #         db_version.version_string
        #     )
        # except Exception as error:
        #     raise errors.InvalidDatabase(
        #         f"Database '{self.db_name}' is not a valid Fishbowl database."
        #     ) from error

        # if release_year > SUPPORTED_UP_TO_RELEASE_YEAR or (
        #     release_year == SUPPORTED_UP_TO_RELEASE_YEAR
        #     and version_number > SUPPORTED_UP_TO_VERSION
        # ):
        #     raise errors.InvalidDatabase(
        #         f"Database version is not supported {db_version.version_string}. Only versions up to {SUPPORTED_UP_TO_VERSION_STRING} are supported."
        #     )

    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"

    @database_url.setter
    def database_url(self):
        raise AttributeError("Cannot set database_url")


from . import utilities
from . import models

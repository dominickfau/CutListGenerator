from __future__ import annotations
import sqlalchemy
import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as session_type_hint
from sqlalchemy.ext.declarative import declarative_base

from cutlistgenerator import (
    DATABASE_URL_WITH_SCHEMA,
    DATABASE_URL_WITHOUT_SCHEMA,
    SCHEMA_NAME,
    SCHEMA_CREATE,
)

backend_logger = logging.getLogger("backend")


engine = create_engine(DATABASE_URL_WITH_SCHEMA)
# type: sqlalchemy.orm.session.sessionmaker
Session = sessionmaker(bind=engine)
global_session = Session()  # type: session_type_hint
DeclarativeBase = declarative_base(
    bind=engine
)  # type: sqlalchemy.ext.declarative.api.DeclarativeMeta


class Base(DeclarativeBase):
    __abstract__ = True
    # __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)

    def to_dict(self) -> dict:
        result = {}
        for column in self.__table__.columns:
            result[column.name] = str(getattr(self, column.name))

        return result


class Auditing(DeclarativeBase):
    __abstract__ = True
    # __table_args__ = {"extend_existing": True}

    date_created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    date_modified = Column(DateTime, nullable=False, default=datetime.datetime.now)


class Status(Base):
    __abstract__ = True
    __table_args__ = {"sqlite_autoincrement": False}

    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<{self.__class__.name}(id={self.id}, name="{self.name}")>'


class Type_(Base):
    __abstract__ = True
    __table_args__ = {"sqlite_autoincrement": False}

    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<{self.__class__.name}(id={self.id}, name="{self.name}")>'


def create_schema() -> None:
    """Create the database schema."""
    backend_logger.info(f"Creating schema [{SCHEMA_NAME}].")
    temp_engine = create_engine(DATABASE_URL_WITHOUT_SCHEMA)
    temp_engine.execute(SCHEMA_CREATE)
    temp_engine.dispose()


def delete_schema() -> None:
    """Delete the database schema."""
    backend_logger.warning(f"Deleting schema [{SCHEMA_NAME}].")
    temp_engine = create_engine(DATABASE_URL_WITHOUT_SCHEMA)
    temp_engine.execute(f"DROP SCHEMA {SCHEMA_NAME}")
    temp_engine.dispose()


def create_tables(session: session_type_hint) -> None:
    """Check if tables exist and create them if not."""
    backend_logger.info("Creating tables.")
    Base.metadata.create_all(bind=session.get_bind())


def disable_foreign_key_checks(session: session_type_hint) -> None:
    """Disable foreign key checks."""
    backend_logger.warning("Disabling foreign key checks.")
    session.execute("SET GLOBAL FOREIGN_KEY_CHECKS = 0;")


def enable_foreign_key_checks(session: session_type_hint) -> None:
    """Enable foreign key checks."""
    backend_logger.warning("Enabling foreign key checks.")
    session.execute("SET GLOBAL FOREIGN_KEY_CHECKS = 1;")


def delete_tabels(session: session_type_hint) -> None:
    """Delete the database tables."""
    backend_logger.warning("Deleting tables.")
    disable_foreign_key_checks(session)
    Base.metadata.drop_all(bind=session.get_bind())
    enable_foreign_key_checks(session)


from .models.user import User, UserLoginEventType
from .models.salesorder import (
    SalesOrderStatus,
    SalesOrderItemStatus,
    SalesOrderItemType,
)
from .models.cutjob import CutJobStatus, CutJobItemStatus
from .models.wirecutter import WireSize, WireCutter
from .models.systemproperty import SystemProperty


def create_default_data() -> None:
    """Create the default data."""
    backend_logger.info("Creating default data.")
    UserLoginEventType.create_default_data()
    User.create_default_data()
    SalesOrderStatus.create_default_data()
    SalesOrderItemStatus.create_default_data()
    SalesOrderItemType.create_default_data()
    CutJobStatus.create_default_data()
    CutJobItemStatus.create_default_data()
    WireSize.create_default_data()
    WireCutter.create_default_data()
    SystemProperty.create_default_data()


def create(force_recreate: bool = False) -> None:
    """Create the database."""
    backend_logger.info("Making sure database exists.")
    with Session() as session:
        try:
            if force_recreate:
                backend_logger.warning("Forcing database recreation.")
                delete_tabels(session)
            create_tables(session)
            create_default_data()
        except sqlalchemy.exc.OperationalError as error:
            if error.orig.args[0] == 1049:  # Unknown database
                backend_logger.info(
                    f"Database {SCHEMA_NAME} does not exist. Creating it."
                )
                create_schema()
                backend_logger.info(f"Database {SCHEMA_NAME} created.")
                backend_logger.info("Recreating database.")
                session.close()
                create()
            else:
                backend_logger.exception("Error creating database tables:\n")
                raise error
        backend_logger.info("Database created.")

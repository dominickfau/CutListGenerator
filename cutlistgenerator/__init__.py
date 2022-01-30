from __future__ import annotations
import os
import logging
from typing import Any
from dataclasses import dataclass
from logging.config import dictConfig
from PyQt5.QtCore import QSettings


@dataclass
class DefaultSetting:
    """Default settings."""

    settings: QSettings
    name: str
    value: Any
    group_name: str = None

    def initialize_setting(self) -> DefaultSetting:
        """Initialize the default setting or pulls the current setting value."""
        if self.group_name:
            self.settings.beginGroup(self.group_name)

        if not self.settings.contains(self.name):
            self.settings.setValue(self.name, self.value)
        else:
            self.value = self.settings.value(self.name)

        if self.group_name:
            self.settings.endGroup()
        return self

    def save(self) -> DefaultSetting:
        """Save the default setting."""
        if self.group_name:
            self.settings.beginGroup(self.group_name)

        self.settings.setValue(self.name, self.value)

        if self.group_name:
            self.settings.endGroup()
        return self


COMPANY_NAME = "DF-Software"
PROGRAM_NAME = "Cut List Generator"
PROGRAM_VERSION = "0.0.1"

settings = QSettings(COMPANY_NAME, PROGRAM_NAME)

USER_HOME_FOLDER = os.path.expanduser("~")
COMPANY_FOLDER = os.path.join(USER_HOME_FOLDER, "Documents", COMPANY_NAME)
PROGRAM_FOLDER = os.path.join(COMPANY_FOLDER, PROGRAM_NAME)
LOG_FOLDER = os.path.join(PROGRAM_FOLDER, "Logs")
LOG_SQLALCHEMY_FOLDER = os.path.join(LOG_FOLDER, "SQLAlchemy")

# Program settings
LAST_USERNAME = DefaultSetting(
    settings=settings, name="last_username", value=""
).initialize_setting()
DEBUG = (
    DefaultSetting(settings=settings, name="debug", value=False)
    .initialize_setting()
    .value
)
if DEBUG == "true":
    DEBUG = True
else:
    DEBUG = False

# Default log settings
MAX_LOG_SIZE_MB = (
    DefaultSetting(
        settings=settings, group_name="Logging", name="max_log_size_mb", value=5
    )
    .initialize_setting()
    .value
)
MAX_LOG_COUNT = (
    DefaultSetting(
        settings=settings, group_name="Logging", name="max_log_count", value=3
    )
    .initialize_setting()
    .value
)
ROOT_LOG_LEVEL = (
    DefaultSetting(
        settings=settings,
        group_name="Logging",
        name="root_log_level",
        value=logging.INFO,
    )
    .initialize_setting()
    .value
)
FRONT_END_LOG_LEVEL = (
    DefaultSetting(
        settings=settings,
        group_name="Logging",
        name="front_end_log_level",
        value=logging.INFO,
    )
    .initialize_setting()
    .value
)
BACK_END_LOG_LEVEL = (
    DefaultSetting(
        settings=settings,
        group_name="Logging",
        name="back_end_log_level",
        value=logging.INFO,
    )
    .initialize_setting()
    .value
)
SQLALCHEMY_ENGINE_LOG_LEVEL = (
    DefaultSetting(
        settings=settings,
        group_name="Logging",
        name="sqlalchemy_engine_log_level",
        value=logging.WARNING,
    )
    .initialize_setting()
    .value
)
SQLALCHEMY_POOL_LOG_LEVEL = (
    DefaultSetting(
        settings=settings,
        group_name="Logging",
        name="sqlalchemy_pool_log_level",
        value=logging.INFO,
    )
    .initialize_setting()
    .value
)
SQLALCHEMY_DIALECT_LOG_LEVEL = (
    DefaultSetting(
        settings=settings,
        group_name="Logging",
        name="sqlalchemy_dialect_log_level",
        value=logging.INFO,
    )
    .initialize_setting()
    .value
)
SQLALCHEMY_ORM_LOG_LEVEL = (
    DefaultSetting(
        settings=settings,
        group_name="Logging",
        name="sqlalchemy_orm_log_level",
        value=logging.INFO,
    )
    .initialize_setting()
    .value
)
FRONT_END_LOG_FILE = "frontend.log"
BACK_END_LOG_FILE = "backend.log"
SQLALCHEMY_ENGINE_LOG_FILE = "sqlalchemy_engine.log"
SQLALCHEMY_POOL_LOG_FILE = "sqlalchemy_pool.log"
SQLALCHEMY_DIALECT_LOG_FILE = "sqlalchemy_dialect.log"
SQLALCHEMY_ORM_LOG_FILE = "sqlalchemy_orm.log"

# Program database settings
FORCE_REBUILD_DATABASE = (
    DefaultSetting(
        settings=settings,
        group_name="Database",
        name="force_rebuild_database",
        value=False,
    )
    .initialize_setting()
    .value
)
if FORCE_REBUILD_DATABASE == "true":
    FORCE_REBUILD_DATABASE = True
else:
    FORCE_REBUILD_DATABASE = False
DATABASE_USER = (
    DefaultSetting(settings=settings, group_name="Database", name="user", value="root")
    .initialize_setting()
    .value
)
DATABASE_PASSWORD = (
    DefaultSetting(
        settings=settings, group_name="Database", name="password", value="Redpurple23"
    )
    .initialize_setting()
    .value
)
DATABASE_HOST = (
    DefaultSetting(
        settings=settings, group_name="Database", name="host", value="localhost"
    )
    .initialize_setting()
    .value
)
DATABASE_PORT = (
    DefaultSetting(settings=settings, group_name="Database", name="port", value="3306")
    .initialize_setting()
    .value
)
SCHEMA_NAME = (
    DefaultSetting(
        settings=settings,
        group_name="Database",
        name="schema",
        value="cutlistgenerator",
    )
    .initialize_setting()
    .value
)
SCHEMA_CREATE = f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"
DATABASE_URL_WITHOUT_SCHEMA = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}"
DATABASE_URL_WITH_SCHEMA = f"{DATABASE_URL_WITHOUT_SCHEMA}/{SCHEMA_NAME}"

# Fishbowl settings
FISHBOWL_DATABASE_USER = (
    DefaultSetting(settings=settings, group_name="Fishbowl", name="user", value="gone")
    .initialize_setting()
    .value
)
FISHBOWL_DATABASE_PASSWORD = (
    DefaultSetting(
        settings=settings, group_name="Fishbowl", name="password", value="fishing"
    )
    .initialize_setting()
    .value
)
FISHBOWL_DATABASE_HOST = (
    DefaultSetting(
        settings=settings, group_name="Fishbowl", name="host", value="localhost"
    )
    .initialize_setting()
    .value
)
FISHBOWL_DATABASE_PORT = (
    DefaultSetting(settings=settings, group_name="Fishbowl", name="port", value="3305")
    .initialize_setting()
    .value
)
FISHBOWL_DATABASE_SCHEMA = (
    DefaultSetting(
        settings=settings, group_name="Fishbowl", name="schema", value="Not Set"
    )
    .initialize_setting()
    .value
)
FISHBOWL_DATABASE_URL = f"mysql+pymysql://{FISHBOWL_DATABASE_USER}:{FISHBOWL_DATABASE_PASSWORD}@{FISHBOWL_DATABASE_HOST}:{FISHBOWL_DATABASE_PORT}/{FISHBOWL_DATABASE_SCHEMA}"

if not os.path.exists(COMPANY_FOLDER):
    os.mkdir(COMPANY_FOLDER)

if not os.path.exists(PROGRAM_FOLDER):
    os.makedirs(PROGRAM_FOLDER)

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

if not os.path.exists(LOG_SQLALCHEMY_FOLDER):
    os.makedirs(LOG_SQLALCHEMY_FOLDER)


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(asctime)s [%(levelname)s] in %(module)s: %(message)s",
            },
            "console": {
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "[%(name)s] %(asctime)s [%(levelname)s] in %(module)s: %(message)s",
            },
        },
        "handlers": {
            "backend_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_FOLDER, BACK_END_LOG_FILE),
                "maxBytes": MAX_LOG_SIZE_MB * 1024 * 1024,
                "backupCount": MAX_LOG_COUNT,
                "formatter": "default",
            },
            "frontend_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_FOLDER, FRONT_END_LOG_FILE),
                "maxBytes": MAX_LOG_SIZE_MB * 1024 * 1024,
                "backupCount": MAX_LOG_COUNT,
                "formatter": "default",
            },
            "console": {"class": "logging.StreamHandler", "formatter": "console"},
        },
        "loggers": {
            "root": {
                "level": ROOT_LOG_LEVEL,
                "handlers": ["backend_log_file", "frontend_log_file", "console"],
            },
            "backend": {
                "level": BACK_END_LOG_LEVEL,
                "handlers": ["backend_log_file", "console"],
            },
            "frontend": {
                "level": FRONT_END_LOG_LEVEL,
                "handlers": ["frontend_log_file", "console"],
            },
        },
    }
)

# Create the loggers
root_logger = logging.getLogger("root")
root_logger.info("=" * 50)
root_logger.info(f"Logging started...")


if DEBUG:
    root_logger.setLevel(logging.DEBUG)
    root_logger.debug("Debug mode enabled.")


from cutlistgenerator import database

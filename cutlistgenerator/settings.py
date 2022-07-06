from __future__ import annotations
import os
import logging
import secrets
from typing import Any
from dataclasses import dataclass
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
PROGRAM_VERSION = "1.0.6"
USER_HOME_FOLDER = os.path.expanduser("~")
COMPANY_FOLDER = os.path.join(USER_HOME_FOLDER, "Documents", COMPANY_NAME)
PROGRAM_FOLDER = os.path.join(COMPANY_FOLDER, PROGRAM_NAME)
LOG_FOLDER = os.path.join(PROGRAM_FOLDER, "Logs")
LOG_SQLALCHEMY_FOLDER = os.path.join(LOG_FOLDER, "SQLAlchemy")


settings = QSettings(COMPANY_NAME, PROGRAM_NAME)

# Program settings
DATE_TIME_FORMAT = "%m-%d-%Y %H:%M"
DATE_FORMAT = "%m-%d-%Y"
DEFAULT_DUE_DATE_PUSH_BACK_DAYS = 30

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


# Logging settings
LOG_FILE = "cutlistgenerator.log"
SQLALCHEMY_ENGINE_LOG_FILE = "sqlalchemy_engine.log"
SQLALCHEMY_POOL_LOG_FILE = "sqlalchemy_pool.log"
SQLALCHEMY_DIALECT_LOG_FILE = "sqlalchemy_dialect.log"
SQLALCHEMY_ORM_LOG_FILE = "sqlalchemy_orm.log"
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
LOG_LEVEL = (
    DefaultSetting(
        settings=settings, group_name="Logging", name="log_level", value=logging.INFO
    )
    .initialize_setting()
    .value
)
if DEBUG:
    LOG_LEVEL = logging.DEBUG


# Database settings
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
        value="cutlistgenerator_new",
    )
    .initialize_setting()
    .value
)
SCHEMA_CREATE = f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"
DATABASE_URL_WITHOUT_SCHEMA = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}"
DATABASE_URL_WITH_SCHEMA = f"{DATABASE_URL_WITHOUT_SCHEMA}/{SCHEMA_NAME}"
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
    DefaultSetting(settings=settings, group_name="Fishbowl", name="schema", value="qes")
    .initialize_setting()
    .value
)
FISHBOWL_DATABASE_URL = f"mysql+pymysql://{FISHBOWL_DATABASE_USER}:{FISHBOWL_DATABASE_PASSWORD}@{FISHBOWL_DATABASE_HOST}:{FISHBOWL_DATABASE_PORT}/{FISHBOWL_DATABASE_SCHEMA}"

# Github settings
GITHUB_USERNAME = "dominickfau"
GITHUB_REPO_NAME = "CutListGenerator"

GITHUB_LATEST_RELEASE_ENDPOINT = (
    f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/releases/latest"
)

# Thread settings
THREAD_UPDATE_INTERVAL = 5  # seconds

# API settings
API_TOKEN_VALIDITY = 1  # days

FLASK_SECRET_KEY = (
    DefaultSetting(
        settings=settings,
        group_name="Flask",
        name="secret_key",
        value=secrets.token_urlsafe(64),
    )
    .initialize_setting()
    .value
)


if not os.path.exists(COMPANY_FOLDER):
    os.mkdir(COMPANY_FOLDER)

if not os.path.exists(PROGRAM_FOLDER):
    os.makedirs(PROGRAM_FOLDER)

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

if not os.path.exists(LOG_SQLALCHEMY_FOLDER):
    os.makedirs(LOG_SQLALCHEMY_FOLDER)

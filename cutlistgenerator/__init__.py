from __future__ import annotations
import os
import logging
from logging.config import dictConfig
from cutlistgenerator.settings import *


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "[%(name)s] %(asctime)s [%(levelname)s] in %(module)s: %(message)s",
            },
            "console": {
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "[%(name)s] %(asctime)s [%(levelname)s] in %(module)s: %(message)s",
            },
        },
        "handlers": {
            "log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_FOLDER, LOG_FILE),
                "maxBytes": MAX_LOG_SIZE_MB * 1024 * 1024,
                "backupCount": MAX_LOG_COUNT,
                "formatter": "default",
            },
            "sqlalchemy_engine_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_SQLALCHEMY_FOLDER, "SQLAlchemy_Engine.log"),
                "maxBytes": MAX_LOG_SIZE_MB * 1024 * 1024,
                "backupCount": MAX_LOG_COUNT,
                "formatter": "default",
            },
            "api_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_FOLDER, LOG_FILE),
                "maxBytes": MAX_LOG_SIZE_MB * 1024 * 1024,
                "backupCount": MAX_LOG_COUNT,
                "formatter": "default",
            },
            "console": {"class": "logging.StreamHandler", "formatter": "console"},
            "sqlalchemy_engine_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_SQLALCHEMY_FOLDER, "SQLAlchemy_Engine.log"),
                "maxBytes": MAX_LOG_SIZE_MB * 1024 * 1024,
                "backupCount": 10,
                "formatter": "default",
            },
            "sqlalchemy_engine_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_SQLALCHEMY_FOLDER, "SQLAlchemy_Engine.log"),
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 10,
                "formatter": "default",
            },
            "sqlalchemy_pool_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_SQLALCHEMY_FOLDER, "SQLAlchemy_Pool.log"),
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 10,
                "formatter": "default",
            },
            "sqlalchemy_dialects_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_SQLALCHEMY_FOLDER, "SQLAlchemy_Dialects.log"),
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 10,
                "formatter": "default",
            },
            "sqlalchemy_orm_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_SQLALCHEMY_FOLDER, "SQLAlchemy_ORM.log"),
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 10,
                "formatter": "default",
            },
        },
        "loggers": {
            "root": {
                "level": LOG_LEVEL,
                "handlers": ["log_file", "console"],
            },
            "backend": {
                "level": LOG_LEVEL,
                "handlers": ["log_file", "console"],
            },
            "frontend": {
                "level": LOG_LEVEL,
                "handlers": ["log_file", "console"],
            },
            "api": {
                "level": LOG_LEVEL,
                "handlers": ["api_log_file", "console"],
            },
            "sqlalchemy.engine": {
                "level": LOG_LEVEL,
                "handlers": ["sqlalchemy_engine_log_file"],
            },
            "sqlalchemy.pool": {
                "level": LOG_LEVEL,
                "handlers": ["sqlalchemy_pool_log_file"],
            },
            "sqlalchemy.dialects": {
                "level": LOG_LEVEL,
                "handlers": ["sqlalchemy_dialects_log_file"],
            },
            "sqlalchemy.orm": {
                "level": LOG_LEVEL,
                "handlers": ["sqlalchemy_orm_log_file"],
            },
        },
    }
)

root_logger = logging.getLogger("root")

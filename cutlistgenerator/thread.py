from __future__ import annotations
import datetime
import time
import threading
import logging
from typing import Callable
from cutlistgenerator import errors

THREAD_UPDATE_INTERVAL = 5  # seconds


backend_logger = logging.getLogger("backend")
functions = []  # type: list[Callable]


def start() -> None:
    """Start threads."""
    backend_logger.info("Starting threads...")
    threading.Thread(target=update, name="Function Caller").start()


def update() -> None:
    """Update all registered functions."""
    for func in functions:
        try:
            func()
        except Exception as e:
            backend_logger.error(f"Error in {func}: {e}")
    threading.Timer(THREAD_UPDATE_INTERVAL, update).start()


def register(func: Callable) -> None:
    """Register a function to be called periodically."""
    if func in functions:
        return
    functions.append(func)


def unregister(func: Callable) -> None:
    """Unregister a function to be called periodically."""
    if func not in functions:
        return
    functions.remove(func)

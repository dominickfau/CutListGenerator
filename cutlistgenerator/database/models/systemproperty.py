from __future__ import annotations
import logging
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import validates

from cutlistgenerator.database import Auditing, Base, global_session

backend_logger = logging.getLogger("backend")


class SystemProperty(Base, Auditing):
    """Represents a system property."""

    __tablename__ = "system_property"

    key = Column(String(256), unique=True)
    value = Column(String(256), nullable=False)
    type_ = Column(String(50), nullable=False)
    read_only = Column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"<SystemProperty(id={self.id}, key={self.key}, value={self.value}, type={self.type_})>"

    def convert_value(self):
        """Converts value from string to type specified in type_."""
        self.value = eval(f"{self.type_}({self.value})")

    @staticmethod
    def find_by_key(key: str) -> SystemProperty:
        """Finds a system property by key. If found convers value before returning."""
        obj = global_session.query(SystemProperty).filter_by(key=key).first()
        if obj:
            obj.convert_value()
        return obj

    # fmt: off
    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        data = [
            SystemProperty(key="Fishbowl Part Department Custom Field Name", value="", type_="string"),
        ]
        for item in data:
            x = (
                global_session.query(SystemProperty)
                .filter(SystemProperty.key == item.key)
                .first()
            )
            if x:
                continue
            global_session.add(item)
            backend_logger.info(f"Creating {item}")
        global_session.commit()

    # fmt: on

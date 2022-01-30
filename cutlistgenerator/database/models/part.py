from __future__ import annotations
from sqlalchemy import Column, String

from cutlistgenerator.database import Auditing, Base, session


class Part(Base, Auditing):
    """Represents a part."""

    __tablename__ = "part"
    __table_args__ = {"extend_existing": True}

    description = Column(String(256), default="")
    number = Column(String(50), unique=True, nullable=False)

    @staticmethod
    def find_by_number(number: str) -> Part:
        """Returns the part with the given number."""
        return session.query(Part).filter(Part.number == number).first()

    @staticmethod
    def from_fishbowl_part(fishbowl_part) -> Part:
        """Creates a new Part from a Fishbowl Part object.
        Or returns an existing Part if it already exists."""
        current_part = Part.find_by_number(fishbowl_part.number)
        if current_part:
            return current_part

        part = Part(number=fishbowl_part.number, description=fishbowl_part.description)
        session.add(part)
        session.commit()
        return part

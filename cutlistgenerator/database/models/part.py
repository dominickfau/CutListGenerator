from __future__ import annotations
from datetime import datetime
import logging
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import collection

from cutlistgenerator.database import Auditing, Base, DeclarativeBase, global_session, session_type_hint
from cutlistgenerator.settings import DEFAULT_DUE_DATE_PUSH_BACK_DAYS

logger = logging.getLogger("backend")

class ParentToChildPart(DeclarativeBase):
    __tablename__ = "parent_to_child_part"

    parent_id = Column(Integer, ForeignKey("part.id"), primary_key=True)
    child_id = Column(Integer, ForeignKey("part.id"), primary_key=True)


class Part(Base, Auditing):
    """Represents a part."""

    __tablename__ = "part"

    description = Column(String(256), default="")
    number = Column(String(256), unique=True, nullable=False)
    excluded_from_import = Column(Boolean, default=False)
    due_date_push_back_days = Column(
        Integer,
        default=DEFAULT_DUE_DATE_PUSH_BACK_DAYS,
        doc="Number of days to push back the due date.",
    )

    # fmt: off
    children = relationship(
        "Part",
        secondary=ParentToChildPart.__table__,
        primaryjoin="Part.id == ParentToChildPart.parent_id",
        secondaryjoin="Part.id == ParentToChildPart.child_id"
    )
    # fmt: on

    @collection.appender
    def add_child(self, child: Part, session: session_type_hint=None) -> None:
        """Append a child part."""
        if not session: session = global_session

        local_object = session.merge(child)
        self.children.append(local_object)
        self.date_modified = datetime.now()
        session.commit()

    @property
    def parent(self) -> Part:
        """Return the parent part."""
        parent_to_child = (
            global_session.query(ParentToChildPart)
            .filter(ParentToChildPart.child_id == self.id)
            .first()
        )
        if parent_to_child is None:
            return None
        return Part.find_by_id(parent_to_child.parent_id)

    def __repr__(self) -> str:
        return f"<Part {self.number}>"
    
    def __str__(self) -> str:
        return self.number

    def set_excluded_from_import(self, excluded_from_import: bool) -> None:
        """Set the excluded_from_import flag."""
        self.excluded_from_import = excluded_from_import
        self.date_modified = datetime.now()
        global_session.commit()

    def set_due_date_push_back_days(self, days: int) -> None:
        """Set the due_date_push_back_days."""
        self.due_date_push_back_days = days
        self.date_modified = datetime.now()
        global_session.commit()

    def set_parent(self, parent: Part) -> None:
        """Set the parent part."""
        self.parent_id = parent.id
        self.date_modified = datetime.now()
        global_session.commit()

    @staticmethod
    def find_by_number(number: str) -> Part:
        """Returns the part with the given number."""
        return global_session.query(Part).filter(Part.number == number).first()

    @staticmethod
    def find_by_id(id: int) -> Part:
        """Returns the part with the given id."""
        return global_session.query(Part).filter(Part.id == id).first()
    
    @staticmethod
    def create(number: str, description: str="", session: session_type_hint=None, skip_commit: bool=False) -> Part:
        """Creates a new part.

        Args:
            number (str): Unique number for this part.
            description (str, optional): Description for this part. Defaults to "".
            session (Session, optional): Session to use for this operation. Defaults to Global Session.

        Returns:
            Part: Returns the newly created part.
        """
        if not session: session = global_session

        if Part.find_by_number(number) is not None:
            raise Exception(f"Part number: {number} is already taken.")

        part = Part(number=number, description=description)
        session.add(part)
        if not skip_commit:
            session.commit()
        logger.debug(f"Creating part {part}")
        return part

    @staticmethod
    def find_all() -> list[Part]:
        """Returns all parts."""
        return global_session.query(Part).order_by(Part.number).all()

    @staticmethod
    def find_all_excluded_from_import() -> list[Part]:
        """Returns all parts that are excluded from import."""
        return (
            global_session.query(Part)
            .filter(Part.excluded_from_import)
            .order_by(Part.number)
            .all()
        )

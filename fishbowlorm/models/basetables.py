from __future__ import annotations
from abc import abstractmethod
from typing import Protocol
from sqlalchemy.orm.session import Session
from sqlalchemy import Column, Integer, String
from fishbowlorm import Base


class ORM(Protocol):
    session: Session


class BaseType(Base):
    """Base class for type tables."""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
    
    @classmethod
    @abstractmethod
    def find_by_name(cls, orm: ORM, name: str) -> BaseType:
        """Find a type by name."""
        pass
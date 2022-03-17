from __future__ import annotations
import logging
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, validates
from cutlistgenerator.database import Base, Type_, global_session
from cutlistgenerator.database.models.part import Part


backend_logger = logging.getLogger("backend")


class LocationType(Type_):
    """Represents a location type."""

    __tablename__ = "location_type"

    @staticmethod
    def find_by_name(name: str) -> LocationType:
        """Find a location type by name."""
        return global_session.query(LocationType).filter_by(name=name).first()

    @staticmethod
    def find_all() -> list[LocationType]:
        """Find all location types."""
        return global_session.query(LocationType).order_by(LocationType.id).all()

    @staticmethod
    def create_default_data() -> list[LocationType]:
        pass


class Location(Base):
    """Represents a location."""

    __tablename__ = "location"

    active = Column(Boolean, nullable=False, default=True)
    default = Column(Boolean, nullable=False, default=False)
    description = Column(String(256), nullable=False)
    name = Column(String(256), nullable=False, unique=True)
    type_id = Column(Integer, ForeignKey("location_type.id"), nullable=False)
    type_ = relationship("LocationType", foreign_keys=[type_id])  # type: LocationType

    @validates("default")
    def validate_default(self, key, value):
        """Validates that only one Location is set as default per location type."""
        if value is None:
            return None
        carton_type = (
            global_session.query(Location)
            .filter_by(default=True, type=self.type_)
            .count()
        )
        if carton_type > 1:
            raise Exception(
                "Only one location can be set as default per location type."
            )
        return value

    @staticmethod
    def find_by_name(name: str) -> Location:
        """Finds a location by name."""
        return global_session.query(Location).filter_by(name=name).first()

    @staticmethod
    def find_all() -> list[Location]:
        """Finds all locations."""
        return global_session.query(Location).order_by(Location.id).all()

    @staticmethod
    def create_default_data() -> list[Location]:
        pass


class DefaultLocation(Base):
    """Represents a default location for a part."""

    __tablename__ = "default_location"
    __table_args__ = (UniqueConstraint("location_id", "part_id"),)

    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    location = relationship("Location", foreign_keys=[location_id])  # type: Location
    part_id = Column(Integer, ForeignKey("part.id"), nullable=False)
    part = relationship("Part", foreign_keys=[part_id])  # type: Part

    @staticmethod
    def find_by_part(part: Part) -> list[DefaultLocation]:
        """Finds all default locations for a part."""
        return global_session.query(DefaultLocation).filter_by(part_id=part.id).all()

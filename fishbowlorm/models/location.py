from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from fishbowlorm import Base
from fishbowlorm.models.basetables import ORM, BaseType
from fishbowlorm.models.customer import FBCustomer
from fishbowlorm.models.vendor import FBVendor


class FBLocationType(BaseType):
    """Location type table."""

    __tablename__ = "locationtype"

    @classmethod
    def find_by_name(cls, orm: ORM, name: str) -> FBLocationType:
        """Find a location type by name."""
        return (
            orm.session.query(FBLocationType)
            .filter(FBLocationType.name == name)
            .first()
        )


class FBLocationGroup(Base):

    __tablename__ = "locationgroup"

    id = Column(Integer, primary_key=True)
    activeFlag = Column(Boolean, nullable=False)
    dateLastModified = Column(DateTime, nullable=False)
    name = Column(String(30), nullable=False)


class FBLocation(Base):

    __tablename__ = "location"

    id = Column(Integer, primary_key=True)
    activeFlag = Column(Boolean, nullable=False)
    countedAsAvailable = Column(Boolean, nullable=False)
    dateLastModified = Column(DateTime, nullable=False)
    defaultCustomerId = Column(Integer, ForeignKey("customer.id"), nullable=False)
    defaultCustomerObj = relationship(
        "FBCustomer", foreign_keys=[defaultCustomerId]
    )  # type: FBCustomer
    defaultFlag = Column(Boolean, nullable=False)
    defaultVendorId = Column(Integer, ForeignKey("vendor.id"), nullable=False)
    defaultVendorObj = relationship(
        "FBVendor", foreign_keys=[defaultVendorId]
    )  # type: FBVendor
    description = Column(String(50), nullable=False)
    locationGroupId = Column(Integer, ForeignKey("locationgroup.id"), nullable=False)
    locationGroupObj = relationship(
        "FBLocationGroup", foreign_keys=[locationGroupId]
    )  # type: FBLocationGroup
    name = Column(String(30), nullable=False)
    parentId = Column(Integer, ForeignKey("location.id"), nullable=False)
    parentObj = relationship("FBLocation", foreign_keys=[parentId])  # type: FBLocation
    pickable = Column(Boolean, nullable=False)
    receivable = Column(Boolean, nullable=False)
    sortOrder = Column(Integer, nullable=False)
    typeId = Column(Integer, ForeignKey("locationtype.id"), nullable=False)
    typeObj = relationship(
        "FBLocationType", foreign_keys=[typeId]
    )  # type: FBLocationType

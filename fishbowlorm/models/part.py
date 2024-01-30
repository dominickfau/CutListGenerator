"""Contains all classes relateing to Parts."""
from __future__ import annotations
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DECIMAL,
    Boolean,
    Index,
    DateTime,
)
from sqlalchemy.orm import relationship
from fishbowlorm import Base
from fishbowlorm.models.basetables import BaseType, ORM
from fishbowlorm.models.uom import FBUom


class FBPartType(BaseType):
    """Represents a part type in Fishbowl."""

    __tablename__ = "parttype"


class FBPartReorderPoint(Base):
    """Represents a part reorder point in Fishbowl."""

    __tablename__ = "partreorder"
    __table_args__ = (
        Index("ix_partreorder_partId", "partId"),
        Index("ix_partreorder_locationGroupId", "locationGroupId"),
    )

    id = Column(Integer, primary_key=True)
    locationGroupId = Column(Integer)
    orderUpToLevel = Column(DECIMAL(28, 9))
    partId = Column(Integer, ForeignKey("part.id"), unique=True)
    reorderPoint = Column(DECIMAL(28, 9))


class FBPart(Base):
    """Represents a part in Fishbowl."""

    __tablename__ = "part"
    __table_args__ = (
        Index("ix_part_id", "id"),
        Index("ix_part_num", "num"),
    )

    id = Column(Integer, primary_key=True)
    abcCode = Column(String(1))
    accountingHash = Column(String(255))
    accountingId = Column(Integer)
    activeFlag = Column(Integer)
    adjustmentAccountId = Column(Integer)
    alertNote = Column(String(255))
    alwaysManufacture = Column(Boolean)
    cogsAccountId = Column(Integer)
    configurable = Column(Integer)
    controlledFlag = Column(Boolean)
    cycleCountTol = Column(DECIMAL(28, 9))
    dateCreated = Column(DateTime)
    dateLastModified = Column(DateTime)
    defaultBomId = Column(Integer, ForeignKey("bom.id"), nullable=True)
    # TODO: Find a way to make this work.
    # defaultBomObj = relationship('FBBom', foreign_keys=[defaultBomId])
    defaultProductId = Column(Integer, ForeignKey("product.id"), nullable=True)
    defaultProductObj = relationship("FBProduct", foreign_keys=[defaultProductId])
    description = Column(String(255))
    details = Column(String(255))
    height = Column(DECIMAL(28, 9))
    inventoryAccountId = Column(Integer)
    lastChangedUser = Column(String(255))
    leadTime = Column(Integer)
    len = Column(DECIMAL(28, 9))
    num = Column(String(255))
    partClassId = Column(Integer)
    products = relationship(
        "FBProduct", foreign_keys="FBProduct.partId", back_populates="partObj"
    )
    pickInUomOfPart = Column(Boolean)
    receivingTol = Column(DECIMAL(28, 9))
    reorderPointObj = relationship("FBPartReorderPoint")  # type: FBPartReorderPoint
    revision = Column(Integer)
    scrapAccountId = Column(Integer)
    serializedFlag = Column(Integer)
    sizeUomId = Column(Integer, ForeignKey("uom.id"))
    sizeUomObj = relationship(
        "FBUom", backref="sizeUom", foreign_keys=[sizeUomId]
    )  # type: FBUom
    stdCost = Column(DECIMAL(28, 9))
    taxId = Column(Integer)
    trackingFlag = Column(Boolean)
    typeId = Column(Integer, ForeignKey("parttype.id"))
    typeObj = relationship("FBPartType", backref="partType")  # type: FBPartType
    uomId = Column(Integer, ForeignKey("uom.id"))
    uomObj = relationship("FBUom", foreign_keys=[uomId])  # type: FBUom
    upc = Column(String(255))
    url = Column(String(255))
    varianceAccountId = Column(Integer)
    weight = Column(DECIMAL(28, 9))
    weightUomId = Column(Integer, ForeignKey("uom.id"))
    weightUomObj = relationship("FBUom", foreign_keys=[weightUomId])  # type: FBUom
    width = Column(DECIMAL(28, 9))

    @property
    def number(self) -> str:
        return self.num

    @property
    def length(self) -> Decimal:
        return self.len

    def __str__(self) -> str:
        return f"{self.id}: {self.num}"

    @staticmethod
    def find_by_number(orm: ORM, number: str) -> FBPart:
        """Find a part by number."""
        return orm.session.query(FBPart).filter(FBPart.num == number).first()

    @staticmethod
    def find_by_id(orm: ORM, id: int) -> FBPart:
        """Find a part by id."""
        return orm.session.query(FBPart).filter(FBPart.id == id).first()

    @staticmethod
    def find_all(orm: ORM) -> FBPart:
        """Find all parts."""
        return orm.session.query(FBPart).order_by(FBPart.num).all()

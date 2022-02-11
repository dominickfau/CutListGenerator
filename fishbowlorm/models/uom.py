"""Contains all classes relateing to Unit of Measures."""

from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Boolean, Index
from sqlalchemy.orm import relationship
from fishbowlorm import Base
from fishbowlorm.models.basetables import BaseType


class FBUomType(BaseType):
    """Represents a Uom type in Fishbowl."""
    __tablename__ = 'uomtype'
    id = Column(Integer, primary_key=True)
    name = Column(String(15))


class FBUom(Base):
    """Represents a Uom in Fishbowl."""
    __tablename__ = 'uom'
    id = Column(Integer, primary_key=True)
    activeFlag = Column(Boolean, default=True)
    code = Column(String(10), nullable=False, unique=True)
    defaultRecord = Column(Boolean, default=False)
    description = Column(String(100), nullable=False)
    integral = Column(Boolean, default=False)
    name = Column(String(50), nullable=False, unique=True)
    readOnly = Column(Boolean, default=False)
    uomType = Column(Integer, ForeignKey('uomtype.id'))
    uomTypeObj = relationship('FBUomType', backref='uom') # type: FBUomType


class FBUomConversion(Base):
    """Represents how to convert from one Uom to another in Fishbowl."""
    __tablename__ = 'uomconversion'
    __table_args__ = (
        Index('ix_uomconversion_fromUomId', 'fromUomId'),
    )


    id = Column(Integer, primary_key=True)
    description = Column(String(100))
    factor = Column(DECIMAL(28, 9),nullable=False)
    fromUomId = Column(Integer, ForeignKey('uom.id'), nullable=False)
    multiply = Column(DECIMAL(28, 9), nullable=False)
    toUomId = Column(Integer, ForeignKey('uom.id'), nullable=False)
    fromUomObj = relationship('FBUom', backref='fromUom', foreign_keys=[fromUomId]) # type: FBUom
    toUomObj = relationship('FBUom', backref='toUom', foreign_keys=[toUomId]) # type: FBUom
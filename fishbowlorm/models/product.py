"""Contains all classes relateing to Products."""
from __future__ import annotations
import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Boolean, DateTime
from sqlalchemy.orm import relationship
from fishbowlorm import Base
from fishbowlorm.models.basetables import ORM
from fishbowlorm.models.part import FBPart
from fishbowlorm.models.uom import FBUom



class FBProduct(Base):
    """Represents a product in Fishbowl."""
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    activeFlag = Column(Integer, nullable=False, default=True)
    alertNote = Column(String(255))
    cartonCount = Column(DECIMAL(28, 9), nullable=False, default=0.0)
    dateCreated = Column(DateTime, nullable=False, default=datetime.datetime.now())
    dateLastModified = Column(DateTime, nullable=False, default=datetime.datetime.now())
    defaultSoItemType = Column(String(255), nullable=False)
    description = Column(String(255))
    details = Column(String(255))
    height = Column(DECIMAL(28, 9))
    kitFlag = Column(Integer, nullable=False, default=False)
    kitGroupedFlag = Column(Integer, nullable=False, default=False)
    len = Column(DECIMAL(28, 9))
    num = Column(String(255), nullable=False, unique=True)
    partId = Column(Integer, ForeignKey('part.id'), nullable=False)
    partObj = relationship('FBPart', foreign_keys=[partId]) # type: FBPart
    price = Column(DECIMAL(28, 9))
    sellableInOtherUoms = Column(Integer, nullable=False, default=False)
    showSoComboFlag = Column(Integer, nullable=False, default=False)
    sizeUomId = Column(Integer, ForeignKey('uom.id'))
    sizeUomObj = relationship('FBUom', foreign_keys=[sizeUomId]) # type: FBUom
    sku = Column(String(255))
    taxableFlag = Column(Integer, nullable=False, default=False)
    uomId = Column(Integer, ForeignKey('uom.id'), nullable=False)
    uomObj = relationship('FBUom', foreign_keys=[uomId]) # type: FBUom
    upc = Column(String(255))
    url = Column(String(255))
    usePriceFlag = Column(Boolean)
    weight = Column(DECIMAL(28, 9))
    weightUomId = Column(Integer, ForeignKey('uom.id'))
    weightUomObj = relationship('FBUom', foreign_keys=[weightUomId]) # type: FBUom
    width = Column(DECIMAL(28, 9))

    @property
    def number(self) -> str:
        return self.num
    
    @property
    def length(self) -> Decimal:
        return self.len
    
    @staticmethod
    def find_by_number(orm: ORM, number: str) -> FBProduct:
        """Finds a product by number."""
        return orm.session.query(FBProduct).filter(FBProduct.num == number).first()
    
    @staticmethod
    def find_all(orm: ORM) -> FBProduct:
        """Find all products."""
        return orm.session.query(FBProduct).order_by(FBProduct.num).all()
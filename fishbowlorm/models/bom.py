from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean, Index
from sqlalchemy.orm import relationship
from fishbowlorm import Base
from fishbowlorm.models.basetables import BaseType, ORM
from fishbowlorm.models.part import FBPart
from fishbowlorm.models.uom import FBUom



class FBAutoCreateType(BaseType):
    """Represents an Auto Create Type for a Bill of Materials in Fishbowl."""
    __tablename__ = 'bomtype'

    @staticmethod
    def find_by_name(orm: ORM, name: str) -> FBAutoCreateType:
        """Find an Auto Create Type by name."""
        return orm.session.query(FBAutoCreateType).filter(FBAutoCreateType.name == name).first()


class FBBom(Base):
    """Represents a Bill of Materials in Fishbowl."""
    __tablename__ = 'bom'
    __table_args__ = (
        Index('ix_bom_autoCreateTypeId', 'autoCreateTypeId'),
        Index('ix_bom_userId', 'userId')
    )
    
    id = Column(Integer, primary_key=True)
    activeFlag = Column(Boolean)
    autoCreateTypeId = Column(Integer, ForeignKey('bomtype.id'))
    autoCreateTypeObj = relationship('FBAutoCreateType', backref='bomAutoCreateType') # type: FBAutoCreateType
    configurable = Column(Boolean)
    dateCreated = Column(DateTime)
    dateLastModified = Column(DateTime)
    description = Column(String(255))
    estimatedDuration = Column(DECIMAL(28, 9))
    note = Column(String(255))
    num = Column(String(255))
    items = relationship('FBBomItem', foreign_keys='FBBomItem.bomId') # type: list[FBBomItem]
    pickFromLocation = Column(Boolean)
    revision = Column(String(30))
    statisticsDateRange = Column(String(40))
    url = Column(String(255))
    userId = Column(Integer, ForeignKey('sysuser.id'))

    @property
    def number(self) -> str:
        return self.num

    @staticmethod
    def find_by_id(orm: ORM, id) -> FBBom:
        if id is None: return None
        return orm.session.query(FBBom).filter_by(id=id).first()
    
    @staticmethod
    def find_by_number(orm: ORM, number) -> FBBom:
        if number is None: return None
        return orm.session.query(FBBom).filter_by(num=number).first()


class FBBomItemType(BaseType):
    """Represents a Bom Item Type in Fishbowl."""
    __tablename__ = 'bomitemtype'

    @staticmethod
    def find_by_name(orm: ORM, name: str):
        return orm.session.query(FBBomItemType).filter_by(name=name).first()


class FBBomItem(Base):
    """Represents an item in a Bom in Fishbowl."""
    __tablename__ = 'bomitem'
    __table_args__ = (
        Index('ix_bomitem_bomId', 'bomId'),
        Index('ix_bomitem_bomItemGroupId', 'bomItemGroupId'),
        Index('ix_bomitem_partId', 'partId'),
        Index('ix_bomitem_typeId', 'typeId'),
        Index('ix_bomitem_uomId', 'uomId')
    )

    id = Column(Integer, primary_key=True)
    addToService = Column(Boolean)
    bomId = Column(Integer, ForeignKey('bom.id'))
    bomItemGroupId = Column(Integer, ForeignKey('bomitemgroup.id'))
    description = Column(String(255))
    groupDefault = Column(Boolean)
    maxQty = Column(DECIMAL(28, 9))
    minQty = Column(DECIMAL(28, 9))
    oneTimeItem = Column(Boolean)
    partId = Column(Integer, ForeignKey('part.id'))
    partObj = relationship('FBPart', foreign_keys=[partId]) # type: FBPart
    priceAdjustment = Column(DECIMAL(28, 9))
    quantity = Column(DECIMAL(28, 9))
    stage = Column(String(255))
    stageBomId = Column(Integer, ForeignKey('bom.id'))
    stageBomObj = relationship('FBBom', backref='bomItemStageBom', foreign_keys=[stageBomId]) # type: FBBom
    typeId = Column(Integer, ForeignKey('bomitemtype.id'))
    typeObj = relationship('FBBomItemType', backref='bomItemType', foreign_keys=[typeId]) # type: FBBomItemType
    uomId = Column(Integer, ForeignKey('uom.id'))
    uomObj = relationship('FBUom', backref='bomItemUom', foreign_keys=[uomId]) # type: FBUom
    useItemLocation = Column(Boolean)
    variableQty = Column(Boolean)
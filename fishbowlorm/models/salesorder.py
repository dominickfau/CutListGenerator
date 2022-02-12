from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean
from fishbowlorm import Base
from fishbowlorm.models.basetables import BaseType, ORM
from fishbowlorm.models.uom import FBUom
from fishbowlorm.models.product import FBProduct
from fishbowlorm.models.customer import FBCustomer



class FBSalesOrderStatus(BaseType):
    __tablename__ = 'sostatus'

    @staticmethod
    def find_by_name(orm: ORM, name: str) -> FBSalesOrderStatus:
        """Find a sales order status by name."""
        return orm.session.query(FBSalesOrderStatus).filter(FBSalesOrderStatus.name == name).first()


class FBSalesOrderType(BaseType):
    __tablename__ = 'sotype'

    @staticmethod
    def find_by_name(orm: ORM, name: str) -> FBSalesOrderType:
        """Find a sales order type by name."""
        return orm.session.query(FBSalesOrderType).filter(FBSalesOrderType.name == name).first()


class FBSalesOrderItemStatus(BaseType):
    __tablename__ = 'soitemstatus'

    @staticmethod
    def find_by_name(orm: ORM, name: str) -> FBSalesOrderItemStatus:
        """Find a sales order item status by name."""
        return orm.session.query(FBSalesOrderItemStatus).filter(FBSalesOrderItemStatus.name == name).first()


class FBSalesOrderItemType(BaseType):
    __tablename__ = 'soitemtype'

    @staticmethod
    def find_by_name(orm: ORM, name: str) -> FBSalesOrderItemType:
        """Find a sales order item type by name."""
        return orm.session.query(FBSalesOrderItemType).filter(FBSalesOrderItemType.name == name).first()


class FBSalesOrder(Base):
    __tablename__ = 'so'

    id = Column(Integer, primary_key=True)
    billToAddress = Column(String(90))
    billToCity = Column(String(30))
    billToCountryId = Column(Integer)
    billToName = Column(String(40))
    billToStateId = Column(Integer)
    billToZip = Column(String(10))
    carrierId = Column(Integer)
    carrierServiceId = Column(Integer)
    cost = Column(DECIMAL(28, 9))
    currencyId = Column(Integer)
    currencyRate = Column(DECIMAL(28, 9))
    customerContact = Column(String(256))
    customerId = Column(Integer, ForeignKey('customer.id'))
    customerObj = relationship('FBCustomer', foreign_keys=[customerId], lazy="joined") # type: FBCustomer
    customerPO = Column(String(25))
    dateCompleted = Column(DateTime)
    dateCreated = Column(DateTime)
    dateExpired = Column(DateTime)
    dateFirstShip = Column(DateTime)
    dateIssued = Column(DateTime)
    dateLastModified = Column(DateTime)
    dateRevision = Column(DateTime)
    email = Column(String(256))
    estimatedTax = Column(DECIMAL(28, 9))
    items = relationship('FBSalesOrderItem', foreign_keys='FBSalesOrderItem.soId') # type: list[FBSalesOrderItem]
    locationGroupId = Column(Integer)
    note = Column(String(256))
    num = Column(String(25))
    paymentTermsId = Column(Integer)
    phone = Column(String(256))
    priorityId = Column(Integer)
    shipToResidential = Column(Integer)
    revisionNum = Column(Integer)
    salesman = Column(String(100))
    salesmanId = Column(Integer)
    salesmanInitials = Column(String(5))
    shipTermsId = Column(Integer)
    shipToAddress = Column(String(255))
    shipToCity = Column(String(255))
    shipToCountryId = Column(Integer)
    shipToName = Column(String(255))
    shipToStateId = Column(Integer)
    shipToZip = Column(String(255))
    statusId = Column(Integer, ForeignKey('sostatus.id'))
    statusObj = relationship('FBSalesOrderStatus', foreign_keys=[statusId]) # type: FBSalesOrderStatus
    taxRate = Column(DECIMAL(28, 9))
    taxRateId = Column(Integer)
    taxRateName = Column(String(30))
    toBeEmailed = Column(Boolean)
    toBePrinted = Column(Boolean)
    totalIncludesTax = Column(Integer)
    totalTax = Column(DECIMAL(28, 9))
    subTotal = Column(DECIMAL(28, 9))
    totalPrice = Column(DECIMAL(28, 9))
    typeId = Column(Integer, ForeignKey('sotype.id'))
    typeObj = relationship('FBSalesOrderType', foreign_keys=[typeId]) # type: FBSalesOrderType
    url = Column(String(256))
    username = Column(String(100))
    vendorPO = Column(String(256))
    dateCalStart = Column(DateTime)
    dateCalEnd = Column(DateTime)

    @property
    def number(self) -> str:
        return self.num
    
    @property
    def dateScheduledFulfillment(self) -> datetime:
        return self.dateFirstShip
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, num={self.num})"
    
    def __str__(self) -> str:
        return f"Sales Order: {self.num}, {self.customerObj.name}, {self.statusObj.name}"
    
    @staticmethod
    def find_all_open(orm: ORM) -> list[FBSalesOrder]:
        """Returns all open sales orders."""
        return orm.session.query(FBSalesOrder).\
                join(FBSalesOrderItem).\
                join(FBSalesOrderStatus).\
                join(FBSalesOrderItemType).\
                filter(FBSalesOrderStatus.id <= FBSalesOrderStatus.find_by_name(orm, "In Progress").id,
                       FBSalesOrderStatus.id >= FBSalesOrderStatus.find_by_name(orm, "Issued").id).\
                all()
    
    @staticmethod
    def find_by_number(orm: ORM, number: str) -> FBSalesOrder:
        """Find a sales order by number."""
        return orm.session.query(FBSalesOrder).filter(FBSalesOrder.num == number).first()


class FBSalesOrderItem(Base):
    __tablename__ = 'soitem'

    id = Column(Integer, primary_key=True)
    adjustAmount = Column(DECIMAL(28, 9))
    adjustPercentage = Column(DECIMAL(28, 9))
    customerPartNum = Column(String(30))
    dateLastFulfillment = Column(DateTime)
    dateLastModified = Column(DateTime)
    dateScheduledFulfillment = Column(DateTime)
    description = Column(String(255))
    exchangeSOLineItem = Column(Integer)
    itemAdjustId = Column(Integer)
    markupCost = Column(DECIMAL(28, 9))
    mcTotalPrice = Column(DECIMAL(28, 9))
    note = Column(String(255))
    productId = Column(Integer, ForeignKey('product.id'))
    productObj = relationship('FBProduct', foreign_keys=[productId]) # type: FBProduct
    productNum = Column(String(30))
    qtyFulfilled = Column(DECIMAL(28, 9))
    qtyOrdered = Column(DECIMAL(28, 9))
    qtyPicked = Column(DECIMAL(28, 9))
    qtyToFulfill = Column(DECIMAL(28, 9))
    revLevel = Column(String(15))
    showItemFlag = Column(Boolean)
    soId = Column(Integer, ForeignKey('so.id'))
    soLineItem = Column(Integer)
    statusId = Column(Integer, ForeignKey('soitemstatus.id'))
    statusObj = relationship('FBSalesOrderItemStatus', foreign_keys=[statusId]) # type: FBSalesOrderItemStatus
    taxId = Column(Integer)
    taxRate = Column(DECIMAL(28, 9))
    taxableFlag = Column(Boolean)
    totalCost = Column(DECIMAL(28, 9))
    totalPrice = Column(DECIMAL(28, 9))
    typeId = Column(Integer, ForeignKey('soitemtype.id'))
    typeObj = relationship('FBSalesOrderItemType', foreign_keys=[typeId]) # type: FBSalesOrderItemType
    unitPrice = Column(DECIMAL(28, 9))
    uomId = Column(Integer, ForeignKey('uom.id'))
    uomObj = relationship('FBUom', foreign_keys=[uomId]) # type: FBUom

    def __str__(self) -> str:
        return f"{self.id}-{self.lineItem}: {self.productObj.number}"

    @property
    def quantityToFulfill(self) -> Decimal:
        """Returns the quantity to fulfill."""
        return self.qtyToFulfill
     
    @property
    def quantityFulfilled(self) -> Decimal:
        """Returns the quantity of the item that has been fulfilled."""
        return self.qtyFulfilled
    
    @property
    def quantityPicked(self) -> Decimal:
        """Returns the quantity picked for this item."""
        return self.qtyPicked
    
    @property
    def quantityOrdered(self) -> Decimal:
        """Returns the quantity ordered."""
        return self.qtyOrdered

    @property
    def quantityLeftToFulfill(self) -> Decimal:
        """Returns the quantity left to fulfill."""
        return self.qtyToFulfill - self.qtyFulfilled - self.qtyPicked if self.uomObj.name != "Each" else round(self.qtyToFulfill - self.qtyFulfilled - self.qtyPicked)
    
    @property
    def lineItem(self) -> int:
        """Returns the line item number."""
        return self.soLineItem
    
    @staticmethod
    def find_by_id(orm: ORM, id: int) -> FBSalesOrderItem:
        """Find a sales order item by id."""
        return orm.session.query(FBSalesOrderItem).filter(FBSalesOrderItem.id == id).first()
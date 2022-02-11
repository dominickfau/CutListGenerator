from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, DateTime, Boolean
from sqlalchemy.orm import relationship
from fishbowlorm import Base
from fishbowlorm.models.basetables import ORM, BaseType
from fishbowlorm.models.user import FBUser


class FBVendorStatus(BaseType):

    __tablename__ = "vendorstatus"

    @classmethod
    def find_by_name(cls, orm: ORM, name: str) -> FBVendorStatus:
        """Find a vendor status by name."""
        return (
            orm.session.query(FBVendorStatus)
            .filter(FBVendorStatus.name == name)
            .first()
        )


class FBVendor(Base):

    __tablename__ = "vendor"

    id = Column(Integer, primary_key=True)
    accountId = Column(Integer, ForeignKey("account.id"), nullable=False)
    # accountObj = relationship('FBAccount', foreign_keys=[accountId]) # type: FBAccount
    accountNum = Column(String(20), nullable=False)
    accountingHash = Column(String(50), nullable=False)
    accountingId = Column(Integer, ForeignKey("accounting.id"), nullable=False)
    activeFlag = Column(Boolean, nullable=False)
    creditLimit = Column(DECIMAL(28, 9), nullable=False)
    currencyId = Column(Integer, ForeignKey("currency.id"), nullable=False)
    # currencyObj = relationship('FBCurrency', foreign_keys=[currencyId]) # type: FBCurrency
    currencyRate = Column(DECIMAL(28, 9), nullable=False)
    dateEntered = Column(DateTime, nullable=False)
    dateLastModified = Column(DateTime, nullable=False)
    defaultCarrierId = Column(Integer, ForeignKey("carrier.id"), nullable=True)
    # defaultCarrierObj = relationship('FBCarrier', foreign_keys=[defaultCarrierId]) # type: FBCarrier
    defaultPaymentTermsId = Column(
        Integer, ForeignKey("paymentterms.id"), nullable=True
    )
    # defaultPaymentTermsObj = relationship('FBPaymentTerms', foreign_keys=[defaultPaymentTermsId]) # type: FBPaymentTerms
    defaultShipTermsId = Column(Integer, ForeignKey("shippingterms.id"), nullable=True)
    # defaultShipTermsObj = relationship('FBShipTerms', foreign_keys=[defaultShipTermsId]) # type: FBShipTerms
    lastChangedUser = Column(Integer, ForeignKey("sysuser.id"), nullable=False)
    lastChangedUserObj = relationship(
        "FBUser", foreign_keys=[lastChangedUser]
    )  # type: FBUser
    leadTime = Column(Integer, nullable=False)
    minOrderAmount = Column(DECIMAL(28, 9), nullable=False)
    name = Column(String(30), nullable=False)
    note = Column(String(50), nullable=False)
    statusId = Column(Integer, ForeignKey("vendorstatus.id"), nullable=False)
    statusObj = relationship(
        "FBVendorStatus", foreign_keys=[statusId]
    )  # type: FBVendorStatus
    sysUserId = Column(Integer, ForeignKey("sysuser.id"), nullable=False)
    sysUserObj = relationship("FBUser", foreign_keys=[sysUserId])  # type: FBUser
    taxRateId = Column(Integer, ForeignKey("taxrate.id"), nullable=True)
    # taxRateObj = relationship('FBTaxRate', foreign_keys=[taxRateId]) # type: FBTaxRate
    url = Column(String(50), nullable=False)

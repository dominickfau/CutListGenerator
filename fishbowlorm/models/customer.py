import datetime
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Boolean
from fishbowlorm import Base



class FBCustomer(Base):
    """Represents a customer in Fishbowl."""
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    # accountId = Column(Integer, ForeignKey('account.id'))
    activeFlag = Column(Integer, default=True)
    creditLimit = Column(DECIMAL(28, 9), default=0.00)
    currencyRate = Column(DECIMAL(28, 9), default=0.00)
    dateCreated = Column(DateTime, default=datetime.datetime.now())
    dateLastModified = Column(DateTime, default=datetime.datetime.now())
    # defaultSalesmanId = Column(Integer, ForeignKey('sysuser.id'))
    jobDepth = Column(Integer)
    lastChangedUser = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    note = Column(String(255))
    number = Column(String(255), unique=True)
    # sysUserId = Column(Integer, ForeignKey('sysuser.id'))
    taxExempt = Column(Boolean, default=False)
    taxExemptNumber = Column(String(255))
    toBeEmailed = Column(Boolean, default=False)
    toBePrinted = Column(Boolean, default=False)
    url = Column(String(255))
    defaultPriorityId = Column(Integer)
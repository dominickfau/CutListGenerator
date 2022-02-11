from __future__ import annotations
from sqlalchemy import Column, Integer, String, Boolean
from fishbowlorm import Base


class FBUser(Base):

    __tablename__ = "sysuser"

    id = Column(Integer, primary_key=True)
    activeFlag = Column(Boolean, nullable=False)
    email = Column(String(255), nullable=False)
    firstName = Column(String(15), nullable=False)
    initials = Column(String(5), nullable=False)
    lastName = Column(String(15), nullable=False)
    phone = Column(String(255), nullable=False)
    userName = Column(String(100), nullable=False)
    userPwd = Column(String(30), nullable=False)

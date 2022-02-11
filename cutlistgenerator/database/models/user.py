from __future__ import annotations
import datetime
import base64
import hashlib
import logging
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Index, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.sqltypes import JSON, BigInteger
from cutlistgenerator import errors
from cutlistgenerator.database import Base, global_session


logged_in_users = {}  # type: dict[str, User]
backend_logger = logging.getLogger("backend")


class User(Base):
    """Represents a user."""

    __tablename__ = "sysuser"
    __table_args__ = (Index("ix_sysuser_username", "username"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    active_flag = Column(Boolean, nullable=False, default=True)
    date_created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    date_last_modified = Column(DateTime, nullable=False, default=datetime.datetime.now)
    email = Column(String(256), nullable=True)
    first_name = Column(String(15), nullable=False)
    last_name = Column(String(15), nullable=False)
    phone = Column(String(256), nullable=True)
    username = Column(String(256), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    properties = relationship(
        "UserProperty", back_populates="user", cascade="all, delete-orphan"
    )  # type: list[UserProperty]

    @staticmethod
    def create_default_data() -> None:
        """Creates all default users."""
        data = [
            User(
                first_name="Admin",
                last_name="User",
                username="admin",
                password_hash=User.generate_password_hash("admin"),
            )
        ]
        for user in data:
            x = (
                global_session.query(User)
                .filter(User.username == user.username)
                .first()
            )
            if x:
                continue
            global_session.add(user)
            backend_logger.info(f"Creating {user}")
        global_session.commit()

    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError("password is not a readable attribute!")

    @property
    def is_superuser(self) -> bool:
        """Check if the user is a superuser."""
        return self.id == 1

    @password.setter
    def password(self, password: str):
        """Hash password on the fly. This allows the plan text password to be used when creating a User instance."""
        self.date_last_modified = datetime.datetime.now()
        self.password_hash = User.generate_password_hash(password)

    @property
    def full_name(self) -> str:
        """Return the full name of the user. In the following format: first_name - last_name"""
        return f"{self.first_name} - {self.last_name}"

    @property
    def initials(self) -> str:
        """Return the initials of the user."""
        return f"{self.first_name[0].upper()}{self.last_name[0].upper()}"

    def verify_password(self, password: str) -> bool:
        """Check if hashed password matches the one provided."""
        return self.password_hash == User.generate_password_hash(password)

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"<User(id={self.id}, username={self.username})>"

    def __str__(self) -> str:
        """Return a string representation of the object."""
        return self.full_name

    @staticmethod
    def find_by_username(username: str) -> User:
        """Find a user by username."""
        return global_session.query(User).filter_by(username=username).first()

    @staticmethod
    def generate_password_hash(password: str) -> str:
        """Generate a hashed password."""
        password = password.strip()
        return base64.b64encode(hashlib.md5(password.encode()).digest()).decode("utf-8")

    @staticmethod
    def authenticate(username: str, password: str) -> User:
        """Authenticate a user."""
        user = User.find_by_username(username)
        if not user:
            raise errors.AuthenticationError("Invalid username or password.")
        if not user.active_flag:
            raise errors.AuthenticationError("This user has been deactivated.")
        if not user.verify_password(password):
            raise errors.AuthenticationError("Invalid username or password.")
        logged_in_users[username] = user
        UserLoginLog.on_login(user)
        return user

    def logout(self):
        """Logout the current user."""
        UserLoginLog.on_logout(self)
        if self.username in logged_in_users:
            del logged_in_users[self.username]

    def save(self) -> None:
        """Save the user to the database."""
        if self.id is None:
            global_session.add(self)

        if self.is_superuser and not self.active_flag:
            raise errors.SaveError("Superuser cannot be deactivated.")
        self.date_last_modified = datetime.datetime.now()
        global_session.commit()

    def delete(self) -> None:
        """Delete the user from the database."""
        if self.is_superuser:
            raise errors.DeleteError("Superuser cannot be deleted.")
        try:
            global_session.delete(self)
            global_session.commit()
        except SQLAlchemyError as e:
            global_session.rollback()
            raise errors.DatabaseError(str(e)) from e


class UserLoginEventType(Base):
    """Represents a user login log event type."""

    __tablename__ = "login_event_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"<UserLoginEventType(id={self.id}, name={self.name})>"

    def __str__(self) -> str:
        """Return a string representation of the object."""
        return self.name

    @staticmethod
    def find_by_name(name: str) -> UserLoginEventType:
        """Find a user login log event type by name."""
        return global_session.query(UserLoginEventType).filter_by(name=name).first()

    @staticmethod
    def find_by_id(id: int) -> UserLoginEventType:
        """Find a user login log event type by id."""
        return global_session.query(UserLoginEventType).filter_by(id=id).first()

    @staticmethod
    def find_all() -> list[UserLoginEventType]:
        """Find all user login log event types."""
        return global_session.query(UserLoginEventType).all()

    @staticmethod
    def create_default_data() -> None:
        """Creates default user login log event types."""
        data = [UserLoginEventType(name="Login"), UserLoginEventType(name="Logout")]
        for event_type in data:
            x = (
                global_session.query(UserLoginEventType)
                .filter(UserLoginEventType.name == event_type.name)
                .first()
            )
            if x:
                continue
            global_session.add(event_type)
            backend_logger.info(f"Creating {event_type}")
        global_session.commit()


class UserLoginLog(Base):
    """A simple log for tracking who logged in or out and when."""

    __tablename__ = "sysuser_login_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    event_type_id = Column(Integer, ForeignKey("login_event_type.id"), nullable=False)
    event_type = relationship(
        "UserLoginEventType", foreign_keys=[event_type_id]
    )  # type: UserLoginEventType
    user_id = Column(Integer, ForeignKey("sysuser.id"), nullable=False)
    user = relationship("User", backref="login_logs", foreign_keys=[user_id])

    @staticmethod
    def on_login(user: User) -> None:
        """Log a login event."""
        global_session.add(
            UserLoginLog(
                event_type_id=UserLoginEventType.find_by_name("Login").id, user=user
            )
        )
        global_session.commit()

    @staticmethod
    def on_logout(user: User) -> None:
        """Log a logout event."""
        global_session.add(
            UserLoginLog(
                event_type_id=UserLoginEventType.find_by_name("Logout").id, user=user
            )
        )
        global_session.commit()


class UserProperty(Base):
    """A user property."""

    __tablename__ = "sysuser_property"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sysuser.id"), nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    name = Column(String(50), nullable=False)
    value = Column(MutableDict.as_mutable(JSON), nullable=False)

    def save(self) -> None:
        """Save the user property to the database."""
        if self.id is None:
            global_session.add(self)
        global_session.commit()

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"<UserProperty(id={self.id}, user_id={self.user_id}, name={self.name}, value={self.value})"

    def __str__(self) -> str:
        """Return a string representation of the object."""
        return f"{self.name}={self.value}"

    @staticmethod
    def find_by_user_id(user_id: int) -> list[UserProperty]:
        """Find all user properties by user id."""
        return global_session.query(UserProperty).filter_by(user_id=user_id).all()

    @staticmethod
    def find_by_user_id_and_property_name(user_id: int, name: str) -> UserProperty:
        """Find a user property by user id and property name."""
        property = (
            global_session.query(UserProperty)
            .filter_by(user_id=user_id, name=name)
            .first()
        )
        if not property:
            property = UserProperty.create(user_id=user_id, name=name, value={})
        return property

    @staticmethod
    def create(user_id: int, name: str, value: dict) -> UserProperty:
        """Create a new user property."""
        obj = UserProperty(user_id=user_id, name=name, value=value)
        global_session.add(obj)
        global_session.commit()
        return obj

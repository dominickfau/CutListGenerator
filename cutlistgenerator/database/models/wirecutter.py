from __future__ import annotations
import logging
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from cutlistgenerator.database import Base, Auditing, global_session


backend_logger = logging.getLogger("backend")


class WireSize(Base):
    """Represents the wire sizes in AWG."""

    __tablename__ = "wire_size"

    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=False)
    awg = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<WireSize(id={self.id}, name={self.name}, awg={self.awg})>"

    @property
    def awg_str(self) -> str:
        return f"{self.awg} AWG"

    @staticmethod
    def find_by_name(name: str) -> WireSize:
        """Find a wire size by name."""
        return global_session.query(WireSize).filter(WireSize.name == name).first()

    @staticmethod
    def find_all() -> list[WireSize]:
        """Find all wire sizes."""
        return global_session.query(WireSize).all()

    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        data = [
            WireSize(name="0 AWG", description="", awg=0),
            WireSize(name="2 AWG", description="", awg=2),
            WireSize(name="4 AWG", description="", awg=4),
            WireSize(name="6 AWG", description="", awg=6),
            WireSize(name="8 AWG", description="", awg=8),
            WireSize(name="10 AWG", description="", awg=10),
            WireSize(name="12 AWG", description="", awg=12),
            WireSize(name="14 AWG", description="", awg=14),
            WireSize(name="16 AWG", description="", awg=16),
            WireSize(name="18 AWG", description="", awg=18),
            WireSize(name="20 AWG", description="", awg=20),
            WireSize(name="22 AWG", description="", awg=22),
            WireSize(name="24 AWG", description="", awg=24),
            WireSize(name="26 AWG", description="", awg=26),
            WireSize(name="28 AWG", description="", awg=28),
            WireSize(name="30 AWG", description="", awg=30),
            WireSize(name="32 AWG", description="", awg=32),
        ]
        for item in data:
            x = (
                global_session.query(WireSize)
                .filter(WireSize.name == item.name)
                .first()
            )
            if x:
                continue
            global_session.add(item)
            backend_logger.info(f"Creating {item}")
        global_session.commit()


class WireCutterOption(Base, Auditing):
    """Represents an option for a wire cutter."""

    __tablename__ = "wire_cutter_option"

    name = Column(String(75), nullable=False, index=True)
    description = Column(String(256))
    wire_cutter_id = Column(
        Integer, ForeignKey("wire_cutter.id"), nullable=False, index=True
    )
    wire_cutter = relationship("WireCutter", back_populates="options")

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, description={self.description!r})"


class WireCutter(Base, Auditing):
    """Represents a wire cutter."""

    __tablename__ = "wire_cutter"

    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(256), default="")
    details = Column(String(256), default="")
    max_wire_size_id = Column(Integer, ForeignKey("wire_size.id"), nullable=False)
    max_wire_size = relationship("WireSize", foreign_keys=[max_wire_size_id])
    max_processing_speed_feet_per_minute = Column(Float, nullable=False, default=0)
    options = relationship("WireCutterOption", back_populates="wire_cutter")

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, description={self.description!r})"

    def save(self) -> None:
        self.date_modified = datetime.datetime.now()
        global_session.commit()

    @staticmethod
    def find_by_name(name: str) -> WireCutter:
        """Returns the wire cutter with the given name."""
        return global_session.query(WireCutter).filter(WireCutter.name == name).first()

    @staticmethod
    def find_by_id(id: int) -> WireCutter:
        """Returns the wire cutter with the given id."""
        return global_session.query(WireCutter).filter(WireCutter.id == id).first()

    @staticmethod
    def find_all() -> list[WireCutter]:
        """Returns all wire cutters."""
        return global_session.query(WireCutter).all()

    @staticmethod
    def create(name: str, max_wire_size: WireSize) -> WireCutter:
        """Creates a new wire cutter."""
        x = global_session.query(WireCutter).filter(WireCutter.name == name).first()
        if x:
            raise Exception(f"Wire cutter {name} already exists")
        wire_cutter = WireCutter(name=name, max_wire_size_id=max_wire_size.id)
        global_session.add(wire_cutter)
        global_session.commit()
        return wire_cutter

    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        data = [WireCutter(id=1, name="Test Cutter", max_wire_size_id=1)]

        for item in data:
            x = (
                global_session.query(WireCutter)
                .filter(WireCutter.id == item.id)
                .first()
            )
            if x:
                continue
            global_session.add(item)
            backend_logger.info(f"Creating {item}")
        global_session.commit()

from __future__ import annotations
import datetime
import logging
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, validates
from cutlistgenerator.database import Base, Auditing, Status, session, Session
from cutlistgenerator.database.models.part import Part
from cutlistgenerator.database.models.salesorder import SalesOrderItem
from cutlistgenerator.database.models.wirecutter import WireCutter

backend_logger = logging.getLogger("backend")


class CutJobStatus(Status):
    """Enum for the status of a cut job."""

    __tablename__ = "cut_job_status"

    def __repr__(self) -> str:
        return f"<CutJobStatus(id={self.id}, name={self.name})>"

    @staticmethod
    def find_all() -> list[CutJobStatus]:
        """Find all CutJobStatus objects."""
        return session.query(CutJobStatus).order_by(CutJobStatus.id).all()

    @staticmethod
    def find_by_id(id: int) -> CutJobStatus:
        return session.query(CutJobStatus).filter(CutJobStatus.id == id).first()

    @staticmethod
    def find_by_name(name: str) -> CutJobStatus:
        return session.query(CutJobStatus).filter(CutJobStatus.name == name).first()

    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        backend_logger.info("Creating default data for CutJobStatus.")
        data = [
            CutJobStatus(id=10, name="Entered"),
            CutJobStatus(id=20, name="In Progress"),
            CutJobStatus(id=30, name="Fulfilled"),
            CutJobStatus(id=40, name="Voided"),
        ]
        for item in data:
            x = session.query(CutJobStatus).filter(CutJobStatus.id == item.id).first()
            if x:
                continue
            session.add(item)
        session.commit()


class CutJobItemStatus(Status):
    """Enum for the status of a cut job item."""

    __tablename__ = "cut_job_item_status"

    def __repr__(self) -> str:
        return f"<CutJobItemStatus(id={self.id}, name={self.name})>"

    @staticmethod
    def find_by_id(id: int) -> CutJobItemStatus:
        return session.query(CutJobItemStatus).filter(CutJobItemStatus.id == id).first()

    @staticmethod
    def find_by_name(name: str) -> CutJobItemStatus:
        return (
            session.query(CutJobItemStatus)
            .filter(CutJobItemStatus.name == name)
            .first()
        )

    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        backend_logger.info("Creating default data for CutJobItemStatus.")
        data = [
            CutJobItemStatus(id=10, name="Entered"),
            CutJobItemStatus(id=20, name="In Progress"),
            CutJobItemStatus(id=30, name="Fulfilled"),
            CutJobItemStatus(id=40, name="On Hold"),
            CutJobItemStatus(id=50, name="Voided"),
        ]
        for item in data:
            x = (
                session.query(CutJobItemStatus)
                .filter(CutJobItemStatus.id == item.id)
                .first()
            )
            if x:
                continue
            session.add(item)
        session.commit()


class CutJob(Base, Auditing):
    """Represents a collection of parts for a WireCutter to prosess."""

    __tablename__ = "cut_job"

    items = relationship(
        "CutJobItem", back_populates="cut_job"
    )  # type: list[CutJobItem]
    """A list of CutJobItems that belong to this CutJob."""
    number = Column(String(100), nullable=False, index=True)
    """A unique number for this CutJob."""
    status_id = Column(
        Integer, ForeignKey("cut_job_status.id"), nullable=False, index=True
    )
    status = relationship(
        "CutJobStatus", foreign_keys=[status_id]
    )  # type: CutJobStatus
    """The status of this CutJob."""
    wire_cutter_id = Column(
        Integer, ForeignKey("wire_cutter.id"), nullable=False, index=True
    )
    wire_cutter = relationship(
        WireCutter, foreign_keys=[wire_cutter_id]
    )  # type: WireCutter
    """The WireCutter that will cut this CutJob."""

    def to_dict(self) -> dict:
        result = {}
        for column in self.__table__.columns:
            result[column.name] = str(getattr(self, column.name))
        result["status"] = self.status.name
        result["wire_cutter"] = self.wire_cutter.to_dict()
        result["items"] = [item.to_dict() for item in self.items]
        result.pop("status_id")
        result.pop("wire_cutter_id")
        return result


class CutJobItem(Base, Auditing):
    """Represents a part needing to be cut."""

    __tablename__ = "cut_job_item"

    cut_job_id = Column(Integer, ForeignKey("cut_job.id"), nullable=False, index=True)
    cut_job = relationship("CutJob", back_populates="items")  # type: CutJob
    date_finished = Column(DateTime, nullable=True, default=None)
    """The date this CutJobItem was finished."""
    part_id = Column(Integer, ForeignKey("part.id"), nullable=False, index=True)
    part = relationship(Part, foreign_keys=[part_id])  # type: Part
    """The Part that is being cut."""
    quantity_cut = Column(Integer, nullable=False, default=0)
    """The quantity of this item that has been cut."""
    quantity_to_cut = Column(Integer, nullable=False, default=0)
    """The quantity of this item that needs to be cut. This equals the total quantity from all linked SalesOrderItems."""
    sales_order_items = relationship(
        "SalesOrderItem", back_populates="cut_job_item"
    )  # type: list[SalesOrderItem]
    status_id = Column(
        Integer, ForeignKey("cut_job_item_status.id"), nullable=False, index=True
    )
    status = relationship(
        "CutJobItemStatus", foreign_keys=[status_id]
    )  # type: CutJobItemStatus
    """The status of this item."""
    total_time_minutes = Column(Integer, nullable=False, default=0)
    """The total time in minutes to cut this item."""

    def to_dict(self) -> dict:
        result = {}
        for column in self.__table__.columns:
            result[column.name] = str(getattr(self, column.name))
        result["status"] = self.status.name
        result["part"] = self.part.to_dict()
        result.pop("part_id")
        result.pop("status_id")

        result["sales_order_numbers"] = [
            f"{item.sales_order.number}:{item.line_number}"
            for item in self.sales_order_items
        ]
        result["sales_order_items"] = [
            item.to_dict() for item in self.sales_order_items
        ]
        return result

    @validates("quantity_cut")
    def validate_quantity_cut(self, key, value: int):
        """Check if the quantity_cut is equal or greater then quantity_to_cut.
        If so set is_cut True for any linked SalesOrderItems."""
        total = 0
        for item in self.sales_order_items:
            total += int(item.quantity_left_to_fulfill)

        finished = value >= total

        if finished:
            self.date_finished = datetime.datetime.now()
            self.date_modified = datetime.datetime.now()

            fulfilled_status = CutJobItemStatus.find_by_name("Fulfilled")
            self.status_id = fulfilled_status.id

            PartCutHistory.create_from_cut_job_item(self, quantity_cut=value)

            job_complete = True
            for item in self.cut_job.items:
                if item.status_id != fulfilled_status.id:
                    job_complete = False
                    break
            if job_complete:
                job_status = CutJobStatus.find_by_name("Fulfilled")
                self.cut_job.status_id = job_status.id
                self.cut_job.date_modified = datetime.datetime.now()

        for item in self.sales_order_items:
            item.set_is_cut(finished)

        return value

    @property
    def fully_cut(self) -> bool:
        """Returns True if the cut job item is fully cut."""
        return self.left_to_cut == 0

    @property
    def left_to_cut(self) -> int:
        """Returns the quantity left to cut."""
        return (
            self.quantity_to_cut - self.quantity_cut
            if self.quantity_to_cut > self.quantity_cut
            else 0
        )

    def add_sales_order_item(self, sales_order_item: SalesOrderItem) -> None:
        """Adds a sales order item to the cut job item."""
        self.sales_order_items.append(sales_order_item)
        self.quantity_to_cut += sales_order_item.quantity_left_to_fulfill
        if self.quantity_to_cut == 0:
            self.status_id = CutJobItemStatus.find_by_name("Fulfilled").id

    def remove_sales_order_item(self, sales_order_item: SalesOrderItem) -> None:
        """Removes a sales order item from the cut job item."""
        self.sales_order_items.remove(sales_order_item)
        self.quantity_to_cut -= sales_order_item.quantity_left_to_fulfill


class PartCutHistory(Base):
    """Holds historical CutJobItem data. Used for to more
    easily estimate the time it takes to cut a part on
    a particular WireCutter."""

    __tablename__ = "part_cut_history"

    event_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    total_time_minutes = Column(Integer, nullable=False)
    part_id = Column(Integer, ForeignKey("part.id"), nullable=False, index=True)
    part = relationship(Part, foreign_keys=[part_id])  # type: Part
    quantity_cut = Column(Integer, nullable=False)
    wire_cutter_id = Column(
        Integer, ForeignKey("wire_cutter.id"), nullable=False, index=True
    )
    wire_cutter = relationship(
        WireCutter, foreign_keys=[wire_cutter_id]
    )  # type: WireCutter

    def to_dict(self) -> dict:
        result = {}
        for column in self.__table__.columns:
            result[column.name] = str(getattr(self, column.name))
        result["part"] = self.part.to_dict()
        result["wire_cutter"] = self.wire_cutter.to_dict()
        result.pop("part_id")
        result.pop("wire_cutter_id")
        return result

    @staticmethod
    def create_from_cut_job_item(item: CutJobItem, quantity_cut=None) -> None:
        with Session() as session:
            history = PartCutHistory(
                part_id=item.part_id,
                wire_cutter_id=item.cut_job.wire_cutter_id,
                quantity_cut=item.quantity_cut
                if quantity_cut is None
                else quantity_cut,
                total_time_minutes=item.total_time_minutes,
            )
            session.add(history)
            session.commit()

    @staticmethod
    def find_by_part(part: Part, session=None) -> list[PartCutHistory]:
        """Finds all PartCutHistory for a given part."""
        if session is None:
            with Session() as session:
                return (
                    session.query(PartCutHistory)
                    .filter(PartCutHistory.part_id == part.id)
                    .order_by(PartCutHistory.event_date.desc())
                    .all()
                )
        return (
            session.query(PartCutHistory)
            .filter(PartCutHistory.part_id == part.id)
            .order_by(PartCutHistory.event_date.desc())
            .all()
        )

    @staticmethod
    def find_by_part_number(number: str, session=None) -> list[PartCutHistory]:
        """Finds all PartCutHistory for a given part number."""
        if session is None:
            with Session() as session:
                part = Part.find_by_number(number)
                if not part:
                    return None
                return PartCutHistory.find_by_part(part, session)
        part = Part.find_by_number(number)
        if not part:
            return None
        return PartCutHistory.find_by_part(part, session)

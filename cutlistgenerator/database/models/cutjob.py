from __future__ import annotations
import datetime
import logging
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, validates
from cutlistgenerator.database import Base, Auditing, Status, global_session, Session
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
        return global_session.query(CutJobStatus).order_by(CutJobStatus.id).all()

    @staticmethod
    def find_by_id(id: int) -> CutJobStatus:
        return global_session.query(CutJobStatus).filter(CutJobStatus.id == id).first()

    @staticmethod
    def find_by_name(name: str) -> CutJobStatus:
        return (
            global_session.query(CutJobStatus).filter(CutJobStatus.name == name).first()
        )

    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        data = [
            CutJobStatus(id=10, name="Entered"),
            CutJobStatus(id=20, name="In Progress"),
            CutJobStatus(id=30, name="Fulfilled"),
            CutJobStatus(id=40, name="Voided"),
        ]
        for item in data:
            x = (
                global_session.query(CutJobStatus)
                .filter(CutJobStatus.id == item.id)
                .first()
            )
            if x:
                continue
            global_session.add(item)
            backend_logger.info(f"Creating {item}")
        global_session.commit()


class CutJobItemStatus(Status):
    """Enum for the status of a cut job item."""

    __tablename__ = "cut_job_item_status"

    @staticmethod
    def find_by_id(id: int) -> CutJobItemStatus:
        return (
            global_session.query(CutJobItemStatus)
            .filter(CutJobItemStatus.id == id)
            .first()
        )

    @staticmethod
    def find_by_name(name: str) -> CutJobItemStatus:
        return (
            global_session.query(CutJobItemStatus)
            .filter(CutJobItemStatus.name == name)
            .first()
        )

    @staticmethod
    def find_all() -> list[CutJobItemStatus]:
        """Find all CutJobItemStatus objects."""
        return (
            global_session.query(CutJobItemStatus).order_by(CutJobItemStatus.id).all()
        )

    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        data = [
            CutJobItemStatus(id=10, name="Entered"),
            CutJobItemStatus(id=20, name="In Progress"),
            CutJobItemStatus(id=30, name="Fulfilled"),
            CutJobItemStatus(id=40, name="On Hold"),
            CutJobItemStatus(id=50, name="Voided"),
        ]
        for item in data:
            x = (
                global_session.query(CutJobItemStatus)
                .filter(CutJobItemStatus.id == item.id)
                .first()
            )
            if x:
                continue
            global_session.add(item)
            backend_logger.info(f"Creating {item}")
        global_session.commit()


class CutJob(Base, Auditing):
    """Represents a collection of parts for a WireCutter to prosess."""

    __tablename__ = "cut_job"
    NUMBER_PREFIX = "CJ"

    items = relationship(
        "CutJobItem", back_populates="cut_job"
    )  # type: list[CutJobItem]
    """A list of CutJobItems that belong to this CutJob."""
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

    @property
    def number(self) -> str:
        return f"{self.NUMBER_PREFIX}{self.id}"

    @staticmethod
    def create(wire_cutter: WireCutter) -> CutJob:
        """Creates a new CutJob."""
        cut_job = CutJob(
            status_id=CutJobStatus.find_by_name("Entered").id,
            wire_cutter_id=wire_cutter.id,
        )
        global_session.add(cut_job)
        global_session.commit()
        return cut_job

    def save(self):
        """Saves the CutJob to the database."""
        if not self.id:
            global_session.add(self)

        self.date_modified = datetime.datetime.now()
        global_session.commit()


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

        for item in self.sales_order_items:
            item.set_is_cut(finished)

        if finished:
            self.date_finished = datetime.datetime.now()

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
        else:
            self.date_finished = None
            self.status_id = CutJobItemStatus.find_by_name("In Progress").id

            job_status = CutJobStatus.find_by_name("In Progress")
            self.cut_job.status_id = job_status.id
            self.cut_job.date_modified = datetime.datetime.now()

        self.date_modified = datetime.datetime.now()
        global_session.commit()
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
        if not self.id:
            global_session.add(self)
            global_session.commit()

        if sales_order_item.cut_job_item_id != self.id:
            self.quantity_to_cut += sales_order_item.quantity_left_to_fulfill
        sales_order_item.set_cut_job_item(self)
        global_session.commit()

    def remove_sales_order_item(self, sales_order_item: SalesOrderItem) -> None:
        """Removes a sales order item from the cut job item."""
        sales_order_item.remove_cut_job_item()
        self.quantity_to_cut -= sales_order_item.quantity_left_to_fulfill
        global_session.commit()

    def save(self):
        """Saves the CutJobItem to the database."""
        if not self.id:
            global_session.add(self)

        self.date_modified = datetime.datetime.now()
        global_session.commit()

    def delete(self):
        """Deletes the CutJobItem from the database."""
        if self.id:
            global_session.delete(self)
        global_session.commit()


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
        history = PartCutHistory(
            part_id=item.part_id,
            wire_cutter_id=item.cut_job.wire_cutter_id,
            quantity_cut=item.quantity_cut if quantity_cut is None else quantity_cut,
            total_time_minutes=item.total_time_minutes,
        )
        global_session.add(history)
        global_session.commit()

    @staticmethod
    def find_by_part(part: Part) -> list[PartCutHistory]:
        """Finds all PartCutHistory for a given part."""
        return (
            global_session.query(PartCutHistory)
            .filter(PartCutHistory.part_id == part.id)
            .order_by(PartCutHistory.event_date.desc())
            .all()
        )

    @staticmethod
    def find_by_part_number(number: str) -> list[PartCutHistory]:
        """Finds all PartCutHistory for a given part number."""
        part = Part.find_by_number(number)
        if not part:
            return None
        return PartCutHistory.find_by_part(part)

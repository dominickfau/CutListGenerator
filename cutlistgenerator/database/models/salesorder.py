from __future__ import annotations
import datetime
import logging
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean
from sqlalchemy.orm import backref, relationship
from cutlistgenerator.database import Auditing, Base, Status, global_session
from cutlistgenerator.database.models.customer import Customer
from cutlistgenerator.database.models.part import Part

backend_logger = logging.getLogger("backend")


class SalesOrderStatus(Status):
    """Represents the status of a sales order."""

    __tablename__ = "sales_order_status"

    def __repr__(self) -> str:
        return f"<SalesOrderStatus(id={self.id}, name='{self.name}')>"

    @staticmethod
    def find_by_id(id: int) -> SalesOrderStatus:
        return (
            global_session.query(SalesOrderStatus)
            .filter(SalesOrderStatus.id == id)
            .first()
        )

    @staticmethod
    def find_all() -> list[SalesOrderStatus]:
        return (
            global_session.query(SalesOrderStatus).order_by(SalesOrderStatus.id).all()
        )

    @staticmethod
    def find_by_name(name: str) -> SalesOrderStatus:
        return (
            global_session.query(SalesOrderStatus)
            .filter(SalesOrderStatus.name == name)
            .first()
        )

    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        data = [
            SalesOrderStatus(id=10, name="Estimate"),
            SalesOrderStatus(id=20, name="Issued"),
            SalesOrderStatus(id=25, name="In Progress"),
            SalesOrderStatus(id=60, name="Fulfilled"),
            SalesOrderStatus(id=70, name="Closed Short"),
            SalesOrderStatus(id=80, name="Voided"),
            SalesOrderStatus(id=90, name="Expired"),
            SalesOrderStatus(id=95, name="Historical"),
        ]
        for item in data:
            x = (
                global_session.query(SalesOrderStatus)
                .filter(SalesOrderStatus.id == item.id)
                .first()
            )
            if x:
                continue
            global_session.add(item)
            backend_logger.info(f"Creating {item}")
        global_session.commit()


class SalesOrderItemStatus(Status):
    """Represents the status of a sales order item."""

    __tablename__ = "sales_order_item_status"

    def __repr__(self) -> str:
        return f"<SalesOrderItemStatus(id={self.id}, name='{self.name}')>"

    @staticmethod
    def find_by_id(id: int) -> SalesOrderItemStatus:
        return (
            global_session.query(SalesOrderItemStatus)
            .filter(SalesOrderItemStatus.id == id)
            .first()
        )

    @staticmethod
    def find_by_name(name: str) -> SalesOrderItemStatus:
        return (
            global_session.query(SalesOrderItemStatus)
            .filter(SalesOrderItemStatus.name == name)
            .first()
        )

    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        data = [
            SalesOrderItemStatus(id=10, name="Entered"),
            SalesOrderItemStatus(id=11, name="Awaiting Build"),
            SalesOrderItemStatus(id=12, name="Building"),
            SalesOrderItemStatus(id=14, name="Built"),
            SalesOrderItemStatus(id=20, name="Picking"),
            SalesOrderItemStatus(id=30, name="Partial"),
            SalesOrderItemStatus(id=40, name="Picked"),
            SalesOrderItemStatus(id=50, name="Fulfilled"),
            SalesOrderItemStatus(id=60, name="Closed Short"),
            SalesOrderItemStatus(id=70, name="Voided"),
            SalesOrderItemStatus(id=75, name="Cancelled"),
            SalesOrderItemStatus(id=95, name="Historical"),
        ]
        for item in data:
            x = (
                global_session.query(SalesOrderItemStatus)
                .filter(SalesOrderItemStatus.id == item.id)
                .first()
            )
            if x:
                continue
            global_session.add(item)
            backend_logger.info(f"Creating {item}")
        global_session.commit()


class SalesOrderItemType(Base):
    """Represents the type of a sales order item."""

    __tablename__ = "sales_order_item_type"

    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<SalesOrderItemType(id={self.id}, name='{self.name}')>"

    @staticmethod
    def find_by_name(name: str) -> SalesOrderItemType:
        return global_session.query(SalesOrderItemType).filter_by(name=name).first()

    @staticmethod
    def create_default_data():
        """Creates the default data for the database."""
        data = [
            SalesOrderItemType(name="Sale"),
            SalesOrderItemType(name="Misc. Sale"),
            SalesOrderItemType(name="Drop Ship"),
            SalesOrderItemType(name="Credit Return"),
            SalesOrderItemType(name="Misc. Credit"),
            SalesOrderItemType(name="Discount Percentage"),
            SalesOrderItemType(name="Discount Amount"),
            SalesOrderItemType(name="Subtotal"),
            SalesOrderItemType(name="Assoc. Price"),
            SalesOrderItemType(name="Shipping"),
            SalesOrderItemType(name="Tax"),
            SalesOrderItemType(name="Kit"),
            SalesOrderItemType(name="Note"),
        ]
        for item in data:
            x = (
                global_session.query(SalesOrderItemType)
                .filter(SalesOrderItemType.name == item.name)
                .first()
            )
            if x:
                continue
            global_session.add(item)
            backend_logger.info(f"Creating {item}")
        global_session.commit()


class SalesOrder(Base, Auditing):
    __tablename__ = "sales_order"

    customer_id = Column(Integer, ForeignKey("customer.id"), index=True)
    customer = relationship("Customer", foreign_keys=[customer_id])  # type: Customer
    date_scheduled_fulfillment = Column(DateTime, nullable=False)
    items = relationship(
        "SalesOrderItem",
        foreign_keys="SalesOrderItem.sales_order_id",
        order_by="SalesOrderItem.line_number",
        back_populates="sales_order",
    )  # type: list[SalesOrderItem]
    number = Column(String(25), unique=True, nullable=False)
    status_id = Column(
        Integer, ForeignKey("sales_order_status.id"), nullable=False, index=True
    )
    status = relationship(
        "SalesOrderStatus", foreign_keys=[status_id]
    )  # type: SalesOrderStatus

    def to_dict(self, include_items=True) -> dict:
        result = {}
        for column in self.__table__.columns:
            result[column.name] = str(getattr(self, column.name))
        result["customer"] = self.customer.to_dict()
        if include_items:
            result["items"] = [item.to_dict() for item in self.items]
        result["status"] = self.status.to_dict()
        result.pop("status_id")
        result.pop("customer_id")
        return result

    @staticmethod
    def find_by_number(number: str) -> SalesOrder:
        return (
            global_session.query(SalesOrder).filter(SalesOrder.number == number).first()
        )

    @staticmethod
    def find_all() -> list[SalesOrder]:
        return global_session.query(SalesOrder).all()

    @staticmethod
    def find_all_unfinished() -> list[SalesOrder]:
        """Returns all sales orders that are not closed."""
        return (
            global_session.query(SalesOrder)
            .filter(
                SalesOrder.status_id <= SalesOrderStatus.find_by_name("In Progress").id
            )
            .order_by(SalesOrder.number)
            .all()
        )


class SalesOrderItem(Base, Auditing):
    __tablename__ = "sales_order_item"

    cut_job_item_id = Column(Integer, ForeignKey("cut_job_item.id"), nullable=True)
    cut_job_item = relationship(
        "CutJobItem", foreign_keys=[cut_job_item_id], back_populates="sales_order_items"
    )
    date_scheduled_fulfillment = Column(DateTime, nullable=False)
    description = Column(String(255))
    fb_so_item_id = Column(Integer, nullable=False)
    is_cut = Column(Boolean, nullable=False, default=False)
    line_number = Column(String(100), nullable=False)
    parent_item_id = Column(Integer, ForeignKey("sales_order_item.id"), nullable=True)
    parent_item = relationship(
        "SalesOrderItem",
        remote_side="SalesOrderItem.id",
        backref=backref("child_items", order_by=line_number),
    )  # type: SalesOrderItem
    part_id = Column(Integer, ForeignKey("part.id"), index=True)
    part = relationship("Part", foreign_keys=[part_id])  # type: Part
    quantity_fulfilled = Column(DECIMAL(28, 9), nullable=False)
    quantity_ordered = Column(DECIMAL(28, 9), nullable=False)
    quantity_picked = Column(DECIMAL(28, 9), nullable=False)
    quantity_to_fulfill = Column(DECIMAL(28, 9), nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales_order.id"), index=True)
    sales_order = relationship(
        "SalesOrder", foreign_keys=[sales_order_id], back_populates="items"
    )  # type: SalesOrder
    status_id = Column(
        Integer, ForeignKey("sales_order_item_status.id"), nullable=False, index=True
    )
    status = relationship(
        "SalesOrderItemStatus", foreign_keys=[status_id]
    )  # type: SalesOrderItemStatus
    type_id = Column(
        Integer, ForeignKey("sales_order_item_type.id"), nullable=False, index=True
    )
    type = relationship(
        "SalesOrderItemType", foreign_keys=[type_id]
    )  # type: SalesOrderItemType

    def __str__(self) -> str:
        return f"{self.id}-{self.line_number}: {self.part.number}"

    def to_dict(self) -> dict:
        result = {}
        for column in self.__table__.columns:
            result[column.name] = str(getattr(self, column.name))
        result["pushed_back_due_date"] = self.pushed_back_due_date.strftime("%Y-%m-%d")
        result["parent_item"] = self.parent_item.to_dict() if self.parent_item else None
        result["part"] = self.part.to_dict()
        result["status"] = self.status.to_dict()
        result["type"] = self.type.to_dict()
        result["sales_order"] = self.sales_order.to_dict(include_items=False)
        result.pop("status_id")
        result.pop("type_id")
        result.pop("part_id")
        return result

    @property
    def parent_order(self) -> SalesOrder:
        """Returns the parent sales order."""
        return (
            global_session.query(SalesOrder)
            .filter(SalesOrder.id == self.sales_order_id)
            .first()
        )

    @property
    def pushed_back_due_date(self) -> datetime.datetime:
        return self.date_scheduled_fulfillment - datetime.timedelta(
            days=self.part.due_date_push_back_days
        )

    @property
    def quantity_left_to_fulfill(self):
        return self.quantity_to_fulfill - self.quantity_fulfilled - self.quantity_picked

    @property
    def is_child(self) -> bool:
        """Returns True if this item is a child item."""
        return self.parent_item_id is not None

    @property
    def fully_cut(self) -> str:
        """Returns True if this item is fully cut."""
        return "Yes" if self.is_cut else "No"

    def set_is_cut(self, is_cut: bool) -> None:
        """Sets the is_cut flag."""
        self.is_cut = is_cut
        self.date_modified = datetime.datetime.now()
        global_session.commit()

    def set_cut_job_item(self, cut_job_item) -> None:
        """Sets the cut job item."""
        self.cut_job_item_id = cut_job_item.id
        self.date_modified = datetime.datetime.now()
        global_session.commit()

    def remove_cut_job_item(self) -> None:
        """Removes the cut job item."""
        self.cut_job_item_id = None
        self.date_modified = datetime.datetime.now()
        global_session.commit()

    @staticmethod
    def find_by_fishbowl_sales_order_item_id(
        self, fb_so_item_id: int
    ) -> list[SalesOrderItem]:
        """Finds all sales order items by the Fishbowl sales order item id."""
        return (
            global_session.query(SalesOrderItem)
            .filter(
                SalesOrderItem.sales_order_id == self.id,
                SalesOrderItem.fb_so_item_id == fb_so_item_id,
            )
            .order_by(SalesOrderItem.line_number)
            .all()
        )

    @staticmethod
    def find_by_fishbowl_so_item_id_line_number(
        fb_so_item_id: int, line_number: str
    ) -> SalesOrderItem:
        """Finds a sales order item by the sales order id and the Fishbowl sales order item id."""
        return (
            global_session.query(SalesOrderItem)
            .filter(
                SalesOrderItem.line_number == line_number,
                SalesOrderItem.fb_so_item_id == fb_so_item_id,
            )
            .first()
        )

    @staticmethod
    def find_by_so_number_line_number(
        so_number: str, line_number: str
    ) -> SalesOrderItem:
        """Finds a sales order item by the sales order id and the Fishbowl sales order item id."""
        return (
            global_session.query(SalesOrderItem)
            .filter(
                SalesOrderItem.line_number == line_number,
                SalesOrderItem.sales_order_id
                == SalesOrder.find_by_number(so_number).id,
            )
            .first()
        )

    @staticmethod
    def remove_part_from_all_items(part: Part) -> int:
        """Removes the part from all sales order items."""
        so_items = (
            global_session.query(SalesOrderItem)
            .filter(SalesOrderItem.part_id == part.id)
            .all()
        )
        total = 0
        for item in so_items:
            total += 1
            global_session.delete(item)
        global_session.commit()
        return total

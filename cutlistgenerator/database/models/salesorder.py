from __future__ import annotations
import datetime
import logging
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import backref, relationship
from cutlistgenerator.database import Auditing, Base, Session, Status, global_session, session_type_hint
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

    def __str__(self) -> str:
        return self.number

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
    def create(number: str, customer: Customer, date_scheduled_fulfillment: datetime.datetime=None, status: SalesOrderStatus=None, session: session_type_hint=None) -> SalesOrder:
        """Creates a new blank sales order.

        Args:
            number (str): A unique number for this order.
            customer (Customer): The customer this order is for.
            date_scheduled_fulfillment (datetime.datetime, optional): Due date for this order. Defaults to current datetime.
            status (SalesOrderStatus, optional): Status for this order. Defaults to Estimate.
            session (Session, optional): Session to use for this operation. Defaults to Global Session.

        Returns:
            SalesOrder: Returns the newly created order.
        """
        if not session: session = global_session
        if not date_scheduled_fulfillment: date_scheduled_fulfillment = datetime.datetime.now()
        if not status: status = SalesOrderStatus.find_by_name("Estimate")

        sales_order = SalesOrder(
            customer_id=customer.id,
            date_scheduled_fulfillment=date_scheduled_fulfillment,
            number=number,
            status_id=status.id,
        )
        session.add(sales_order)
        session.commit()
        backend_logger.debug(f"Creating sales order {sales_order}.")
        return sales_order

    @staticmethod
    def find_by_number(number: str) -> SalesOrder:
        """Finds a sales order by number.

        Args:
            number (str): Sales Order number to find.

        Returns:
            SalesOrder: Returns the sales order if found, else None
        """
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

    @staticmethod
    def remove_empty_orders():
        """Removes all sales orders that have no items."""
        orders = global_session.query(SalesOrder).all()
        for order in orders:
            if not order.items:
                global_session.delete(order)
        global_session.commit()


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
    quantity_fulfilled = Column(Float, nullable=False)
    quantity_ordered = Column(Float, nullable=False)
    quantity_picked = Column(Float, nullable=False)
    quantity_to_fulfill = Column(Float, nullable=False)
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
        return f"Id: {self.id} Line: {self.line_number} Part: {self.part.number}"

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
    def has_cut_job_item(self) -> bool:
        """Returns True if this item has a cut job item."""
        return self.cut_job_item is not None

    @property
    def has_cut_job_item_string(self) -> str:
        """Returns a string indicating whether this item has a cut job item."""
        return "Yes" if self.has_cut_job_item else "No"

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
    
    def delete(self) -> None:
        """Deletes the item from DB."""
        removed_so_item = RemovedSalesOrderItem.create_from_so_item(self)
        removed_cut_job_item = None
        try:
            if self.parent_item:
                backend_logger.info(f"Deleting parent SO item {self.parent_item}")
                self.parent_item.delete()

            if self.cut_job_item:
                backend_logger.info(f"Deleting Cut Job Item {self.cut_job_item}")
                cut_job_item = self.cut_job_item
                self.cut_job_item_id = None
                global_session.commit()
                removed_cut_job_item = cut_job_item.delete()
            backend_logger.info(f"Deleting So Item {self}")
            global_session.delete(self)
            global_session.commit()
        except Exception as e:
            global_session.delete(removed_so_item)
            if removed_cut_job_item:
                global_session.delete(removed_cut_job_item)
            global_session.commit()
            raise e

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
    def find_by_id(item_id: int) -> SalesOrderItem:
        return global_session.query(SalesOrderItem).filter(SalesOrderItem.id == item_id).first()

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
        SalesOrder.remove_empty_orders()
        return total

    @staticmethod
    def set_is_cut_for_all_parts(part: Part) -> int:
        """Sets the is cut flag for all items with this part."""
        so_items = (
            global_session.query(SalesOrderItem)
            .filter(SalesOrderItem.part_id == part.id)
            .all()
        )
        total = 0
        for item in so_items:
            total += 1
            item.set_is_cut(True)
        return total
    
    @staticmethod
    def create(
            part: Part,
            sales_order: SalesOrder,
            description: str,
            quantity_fulfilled: float,
            quantity_ordered: float,
            quantity_picked: float,
            quantity_to_fulfill: float,
            line_number: str,
            date_scheduled_fulfillment: datetime.datetime=None,
            fb_so_item_id: int=None,
            status: SalesOrderItemStatus=None,
            type: SalesOrderItemType=None
        ) -> SalesOrderItem:

        if not date_scheduled_fulfillment: date_scheduled_fulfillment = datetime.datetime.now()
        if not status: status = SalesOrderItemStatus.find_by_name("Entered")
        if not type: type = SalesOrderItemType.find_by_name("Sale")

        sales_order_item = SalesOrderItem(
            part_id=part.id,
            sales_order_id=sales_order.id,
            date_scheduled_fulfillment=date_scheduled_fulfillment,
            description=description,
            fb_so_item_id=fb_so_item_id,
            quantity_fulfilled=quantity_fulfilled,
            quantity_ordered=quantity_ordered,
            quantity_picked=quantity_picked,
            quantity_to_fulfill=quantity_to_fulfill,
            line_number=line_number,
            status_id=status.id,
            type_id=type.id,
        )
        global_session.add(sales_order_item)
        global_session.commit()
        backend_logger.debug(f"Creating sales order item {sales_order_item}.")


class RemovedSalesOrderItem(Base):
    __tablename__ = "removed_sales_order_item"

    cut_job_item_id = Column(Integer)
    date_scheduled_fulfillment = Column(DateTime)
    description = Column(String(255))
    fb_so_item_id = Column(Integer)
    is_cut = Column(Boolean, default=False)
    line_number = Column(String(100))
    parent_item_id = Column(Integer)
    part_id = Column(Integer, ForeignKey("part.id"))
    quantity_fulfilled = Column(Float)
    quantity_ordered = Column(Float)
    quantity_picked = Column(Float)
    quantity_to_fulfill = Column(Float)
    sales_order_id = Column(Integer)
    status_id = Column(Integer)
    type_id = Column(Integer)

    @staticmethod
    def create_from_so_item(soitem: SalesOrderItem) -> RemovedSalesOrderItem:
        item = RemovedSalesOrderItem(
            cut_job_item_id = soitem.cut_job_item_id,
            date_scheduled_fulfillment = soitem.date_scheduled_fulfillment,
            description = soitem.description,
            fb_so_item_id = soitem.fb_so_item_id,
            is_cut = soitem.is_cut,
            line_number = soitem.line_number,
            parent_item_id = soitem.parent_item_id,
            part_id = soitem.part_id,
            quantity_fulfilled = soitem.quantity_fulfilled,
            quantity_ordered = soitem.quantity_ordered,
            quantity_picked = soitem.quantity_picked,
            quantity_to_fulfill = soitem.quantity_to_fulfill,
            sales_order_id = soitem.sales_order_id,
            status_id = soitem.status_id,
            type_id = soitem.type_id
        )

        global_session.add(item)
        global_session.commit()
        return item
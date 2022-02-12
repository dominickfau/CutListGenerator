from __future__ import annotations
import time
import logging
<<<<<<< HEAD
from fishbowlorm.models import FBCustomer, FBSalesOrder
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from cutlistgenerator.database import Base, Auditing, global_session
=======
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from cutlistgenerator.database import Base, Auditing, session
>>>>>>> d46f4b350d54fc3183be302d62ac1458f071c414


backend_logger = logging.getLogger("backend")


class CustomerNameConversion(Base, Auditing):
    """Represents a customer name conversion."""

    __tablename__ = "customer_name_conversion"

    customer_id = Column(Integer, ForeignKey("customer.id"), unique=True)
    name = Column(String(255), nullable=False, index=True)


class Customer(Base, Auditing):
    """Represents a customer."""

    __tablename__ = "customer"

    name = Column(String(255), nullable=False, unique=True)
    name_convertion = relationship(
        "CustomerNameConversion",
        foreign_keys="CustomerNameConversion.customer_id",
        uselist=False,
        lazy="joined",
    )  # type: CustomerNameConversion

    def to_dict(self) -> dict:
        result = {}
        for column in self.__table__.columns:
            result[column.name] = str(getattr(self, column.name))
        result["name_converted"] = self.name_converted
        return result

    @property
    def name_converted(self) -> str:
        """Returns the name converted. If no conversion is found, the original name is returned."""
        name = self.name
        if self.name_convertion:
            name = (
                self.name_convertion.name
                if len(self.name_convertion.name) > 0
                else self.name
            )
        return name

    @staticmethod
    def find_by_name(name: str) -> Customer:
        """Returns the customer with the given name."""
        return global_session.query(Customer).filter(Customer.name == name).one()

    @staticmethod
    def find_all() -> list[Customer]:
        """Returns all customers."""
        return global_session.query(Customer).all()

    @staticmethod
    def create_from_fishbowl_sales_orders(
        fishbowl_sales_orders: list[FBSalesOrder],
    ) -> None:
        """Creates a customer from the given sales orders."""
        s = time.perf_counter()
        created = 0
        customer_names = [
            customer.name for customer in Customer.find_all(global_session)
        ]
        for fb_sales_order in fishbowl_sales_orders:
            if fb_sales_order.customerObj.name in customer_names:
                continue
            customer = Customer(name=fb_sales_order.customerObj.name)
            customer_names.append(customer.name)
            global_session.add(customer)
            global_session.commit()
            created += 1
        backend_logger.debug(
            f"[EXECUTION TIME] Created {created} customers in {time.perf_counter() - s} seconds."
        )

    @staticmethod
    def from_fishbowl_customer(fishbowl_customer: FBCustomer) -> Customer:
        """Creates a new Customer from a Fishbowl Customer object.
        Or returns an existing Customer if it already exists."""
        current_customer = Customer.find_by_name(fishbowl_customer.name)
        if current_customer:
            return current_customer

        customer = Customer(name=fishbowl_customer.name)
        global_session.add(customer)
        global_session.commit()
        return customer

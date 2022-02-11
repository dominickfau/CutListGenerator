from __future__ import annotations
import datetime
import functools
import time
import logging
from typing import Callable
from PyQt5.QtWidgets import QLineEdit
from fishbowlorm import utilities as fb_utilities
from fishbowlorm import models as fb_models
from fishbowlorm.models.basetables import ORM
from fishbowlorm.models.salesorder import FBSalesOrder
from cutlistgenerator.customwidgets.qtable import CustomQTableWidget
from cutlistgenerator.database import session_type_hint
from cutlistgenerator.database.models.part import Part
from cutlistgenerator.database.models.customer import Customer
from cutlistgenerator.database.models.salesorder import (
    SalesOrder,
    SalesOrderItemStatus,
    SalesOrderItemType,
    SalesOrderStatus,
    SalesOrderItem,
)

backend_logger = logging.getLogger("backend")


def clean_text_input(widget: QLineEdit):
    """Removes leading and trailing whitespace from a QLineEdit."""
    widget.setText(widget.text().strip())


def date_format(date: datetime.datetime) -> str:
    """Convert a datetime object to a string."""
    return date.strftime("%m/%d/%Y")


def create_sales_orders_from_fishbowl_data(
    session: session_type_hint,
    fishbowl_orm: ORM,
    fb_open_sales_orders: list[FBSalesOrder],
    progress_signal=None,
    progress_data_signal=None,
) -> None:
    """Create or updates sales orders from Fishbowl data.

    Args:
        session (session_type_hint): The database session to use.
        fishbowl_orm (ORM): The Fishbowl ORM to use.
        fb_open_sales_orders (list[FBSalesOrder]): The list of open Fishbowl sales orders to process.
        progress_signal ([type], optional): PyQt5 signal to emit progress updates. This will be the % complete. Defaults to None.
        progress_data_signal ([type], optional): PyQt5 signal to emit progress updates. This will be the message displayed on the progress bar. Defaults to None.
    """
    backend_logger.info("=" * 80)
    backend_logger.info("Creating / Updating SalesOrder objects from Fishbowl data.")

    child_parts = {}  # type: dict[Part, list[Part]]
    customers = (
        {}
    )  # type: dict[Customer.name, Customer] # This is used to keep track of customers that have been created.

    total = len(fb_open_sales_orders)
    backend_logger.info(f"{total} sales orders to process.")

    backend_logger.info("Pulling all current customers.")
    for customer in Customer.find_all():
        customers[customer.name] = customer

    backend_logger.info(f"{len(customers)} customers currently exist.")

    backend_logger.info("Processing Fishbowl sales orders.")
    for index, fishbowl_sales_order in enumerate(fb_open_sales_orders):
        backend_logger.debug(f"Processing sales order {fishbowl_sales_order.number}")

        if progress_signal is not None:
            value = index / total * 100
            progress_signal.emit(value)

        if progress_data_signal is not None:
            progress_data_signal.emit(
                f"Processing sales order {fishbowl_sales_order.number} ({index}/{total})"
            )

        try:
            customer = customers[fishbowl_sales_order.customerObj.name]
        except KeyError:
            customer = None

        if customer is None:
            customer = Customer(name=fishbowl_sales_order.customerObj.name)
            backend_logger.info(f"Creating customer {customer.name}.")
            session.add(customer)
            session.commit()
            customers[fishbowl_sales_order.customerObj.name] = customer

        sales_order = SalesOrder.find_by_number(fishbowl_sales_order.number)
        if sales_order is None:
            sales_order = SalesOrder(
                customer=customer,
                date_scheduled_fulfillment=fishbowl_sales_order.dateScheduledFulfillment,
                number=fishbowl_sales_order.number,
                status_id=SalesOrderStatus.find_by_name(
                    fishbowl_sales_order.statusObj.name
                ).id,
            )
            session.add(sales_order)
            session.commit()

        sales_order.date_modified = datetime.datetime.now()
        sales_order.status_id = SalesOrderStatus.find_by_name(
            fishbowl_sales_order.statusObj.name
        ).id
        session.commit()

        for fishbowl_sales_order_item in fishbowl_sales_order.items:
            if not fishbowl_sales_order_item.productObj:
                continue
            parent_part = fishbowl_sales_order_item.productObj.partObj

            part = Part.find_by_number(parent_part.number)
            if part is None:
                part = Part.from_fishbowl_part(parent_part)

            sales_order_item = SalesOrderItem.find_by_fishbowl_so_item_id_line_number(
                fishbowl_sales_order_item.id, fishbowl_sales_order_item.lineItem
            )

            if sales_order_item is None:
                sales_order_item = SalesOrderItem(
                    part_id=part.id,
                    sales_order_id=sales_order.id,
                    date_scheduled_fulfillment=fishbowl_sales_order_item.dateScheduledFulfillment,
                    description=fishbowl_sales_order_item.description,
                    fb_so_item_id=fishbowl_sales_order_item.id,
                    quantity_fulfilled=fishbowl_sales_order_item.quantityFulfilled,
                    quantity_ordered=fishbowl_sales_order_item.quantityOrdered,
                    quantity_picked=fishbowl_sales_order_item.quantityPicked,
                    quantity_to_fulfill=fishbowl_sales_order_item.quantityToFulfill,
                    line_number=fishbowl_sales_order_item.lineItem,
                    status_id=SalesOrderItemStatus.find_by_name(
                        fishbowl_sales_order_item.statusObj.name
                    ).id,
                    type_id=SalesOrderItemType.find_by_name(
                        fishbowl_sales_order_item.typeObj.name
                    ).id,
                )
                session.add(sales_order_item)
                session.commit()

            if parent_part in child_parts:
                fb_child_parts = child_parts[parent_part]
            else:
                child_parts[
                    parent_part
                ] = fb_child_parts = fb_utilities.get_child_parts(
                    fishbowl_orm, parent_part
                )

            for index, fb_child_part in enumerate(fb_child_parts):
                child_part = Part.find_by_number(fb_child_part.number)
                if child_part is None:
                    child_part = Part.from_fishbowl_part(fb_child_part)

                line_number = f"{fishbowl_sales_order_item.lineItem}.{index + 1}"
                child_sales_order_item = (
                    SalesOrderItem.find_by_fishbowl_so_item_id_line_number(
                        fishbowl_sales_order_item.id, line_number
                    )
                )

                if child_sales_order_item is None:
                    child_sales_order_item = SalesOrderItem(
                        part_id=child_part.id,
                        sales_order_id=sales_order.id,
                        date_scheduled_fulfillment=fishbowl_sales_order_item.dateScheduledFulfillment,
                        description=fishbowl_sales_order_item.description,
                        fb_so_item_id=fishbowl_sales_order_item.id,
                        quantity_fulfilled=fishbowl_sales_order_item.quantityFulfilled,
                        quantity_ordered=fishbowl_sales_order_item.quantityOrdered,
                        quantity_picked=fishbowl_sales_order_item.quantityPicked,
                        quantity_to_fulfill=fishbowl_sales_order_item.quantityToFulfill,
                        line_number=line_number,
                        parent_item_id=sales_order_item.id,
                        status_id=SalesOrderItemStatus.find_by_name(
                            fishbowl_sales_order_item.statusObj.name
                        ).id,
                        type_id=SalesOrderItemType.find_by_name(
                            fishbowl_sales_order_item.typeObj.name
                        ).id,
                    )
                    session.add(child_sales_order_item)
                    session.commit()


def update_unfinished_sales_orders(
    session: session_type_hint, fishbowl_orm: ORM
) -> None:
    for sales_order in SalesOrder.find_all_unfinished():
        fb_sales_order = fb_models.FBSalesOrder.find_by_number(
            fishbowl_orm, sales_order.number
        )
        if fb_sales_order is None:
            continue

        sales_order.date_modified = datetime.datetime.now()
        sales_order.status_id = SalesOrderStatus.find_by_name(
            fb_sales_order.statusObj.name
        ).id
        session.commit()

        for item in sales_order.items:
            fb_sales_order_item = fb_models.FBSalesOrderItem.find_by_id(
                fishbowl_orm, item.fb_so_item_id
            )
            if fb_sales_order_item is None:
                continue

            part = Part.find_by_number(fb_sales_order_item.productObj.partObj.number)

            item.date_modified = datetime.datetime.now()
            item.date_scheduled_fulfillment = (
                fb_sales_order_item.dateScheduledFulfillment
            )
            item.part_id = part.id
            item.quantity_fulfilled = fb_sales_order_item.quantityFulfilled
            item.quantity_ordered = fb_sales_order_item.quantityOrdered
            item.quantity_picked = fb_sales_order_item.quantityPicked
            item.quantity_to_fulfill = fb_sales_order_item.quantityToFulfill
            item.status_id = SalesOrderItemStatus.find_by_name(
                fb_sales_order_item.statusObj.name
            ).id
            item.type_id = SalesOrderItemType.find_by_name(
                fb_sales_order_item.typeObj.name
            ).id
            session.commit()


def debug_run_time(function: Callable):
    """Decorator for adding timming info to functions."""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = function(*args, **kwargs)
        end = time.perf_counter()
        print("=" * 80)
        print(f"{function.__name__}: {end - start}")
        return result

    return wrapper


def on_column_visibility_changed(index: int, visible: bool):
    """Update the users properties when a column is hidden or shown."""
    items = []  # type: list[int]

    if visible:
        items.remove(index)
    else:
        items.append(index)


def remove_hidden_columns(table_widget: CustomQTableWidget):
    """Remove hidden columns from the table view."""
    partSearchRemovedHeaders = []  # type: list[int]
    for index in partSearchRemovedHeaders:
        table_widget.setColumnHidden(index, True)
        table_widget.header_context_menu.actions()[index + 1].setChecked(
            False
        )  # Add 1 to the index because table columns start at 0.

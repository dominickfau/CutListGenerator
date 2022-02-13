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


def debug_run_time(function: Callable, logger: logging.Logger = backend_logger):
    """Decorator for adding timming info to functions.

    Args:
        function (Callable): The function to time.
        logger (logging.Logger, optional): The logger to use. Defaults to backend_logger.
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = function(*args, **kwargs)
        end = time.perf_counter()
        # logger.warning("=" * 80)
        logger.warning(f"[EXECUTION TIME] Function: {function.__name__}: {end - start}")
        return result

    return wrapper


def clean_text_input(widget: QLineEdit):
    """Removes leading and trailing whitespace from a QLineEdit."""
    widget.setText(widget.text().strip())


def date_format(date: datetime.datetime) -> str:
    """Convert a datetime object to a string."""
    return date.strftime("%m/%d/%Y")


# This line keeps black magic from happening.
# fmt: off
@debug_run_time
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

    child_parts = {} # type: dict[fb_models.FBPart, list[fb_models.FBPart]] # Used to store child parts for parent parts that have been processed.
    customers = {} # type: dict[Customer.name, Customer] # Used to keep track of customers that have been created.
    total = len(fb_open_sales_orders)
    backend_logger.info(f"{total} sales orders to process.")

    backend_logger.info("Pulling all current customers.")
    for customer in Customer.find_all():
        customers[customer.name] = customer

    backend_logger.info(f"{len(customers)} customers currently exist.")

    backend_logger.info("Processing Fishbowl sales orders.")
    for index, fishbowl_sales_order in enumerate(fb_open_sales_orders):
        fb_so_number = fishbowl_sales_order.number
        fb_so_status_name = fishbowl_sales_order.statusObj.name
        fb_cutomer_name = fishbowl_sales_order.customerObj.name
        loading_bar_value = int(index / total * 100)
        loading_bar_message = f"Processing sales order {fb_so_number} ({index}/{total})"

        backend_logger.debug(f"Processing sales order {fb_so_number}")

        if progress_signal is not None: progress_signal.emit(loading_bar_value)
        if progress_data_signal is not None: progress_data_signal.emit(loading_bar_message)

        # Create the customer if it doesn't exist.
        try:
            customer = customers[fb_cutomer_name]
        except KeyError:
            customer = Customer(name=fb_cutomer_name)
            backend_logger.info(f"Creating customer {customer.name}.")
            session.add(customer)
            session.commit()
            customers[fb_cutomer_name] = customer

        # Find the sales order, or create it if it doesn't exist.
        sales_order = SalesOrder.find_by_number(fb_so_number)
        if sales_order is None:
            sales_order = SalesOrder(
                customer=customer,
                date_scheduled_fulfillment=fishbowl_sales_order.dateScheduledFulfillment,
                number=fb_so_number,
                status_id=SalesOrderStatus.find_by_name(fb_so_status_name).id,
            )
            backend_logger.debug(f"Creating sales order {sales_order.number}.")
            session.add(sales_order)
            session.commit()

        sales_order.date_modified = datetime.datetime.now()
        sales_order.status_id = SalesOrderStatus.find_by_name(fb_so_status_name).id
        session.commit()

        for fb_so_item in fishbowl_sales_order.items:
            # Find the sales order item, or create it if it doesn't exist.
            if not fb_so_item.productObj: continue
            fb_parent_part = fb_so_item.productObj.partObj
            backend_logger.debug(f"Processing item {fb_so_item}.")

            part = Part.find_by_number(fb_parent_part.number)
            if part is None:
                part = Part.from_fishbowl_part(fb_parent_part)

            sales_order_item = SalesOrderItem.find_by_fishbowl_so_item_id_line_number(fb_so_item.id, fb_so_item.lineItem)

            if sales_order_item is None and not part.excluded_from_import: # This keeps excluded parts from being imported.
                sales_order_item = SalesOrderItem(
                    part_id=part.id,
                    sales_order_id=sales_order.id,
                    date_scheduled_fulfillment=fb_so_item.dateScheduledFulfillment,
                    description=fb_so_item.description,
                    fb_so_item_id=fb_so_item.id,
                    quantity_fulfilled=fb_so_item.quantityFulfilled,
                    quantity_ordered=fb_so_item.quantityOrdered,
                    quantity_picked=fb_so_item.quantityPicked,
                    quantity_to_fulfill=fb_so_item.quantityToFulfill,
                    line_number=fb_so_item.lineItem,
                    status_id=SalesOrderItemStatus.find_by_name(
                        fb_so_item.statusObj.name
                    ).id,
                    type_id=SalesOrderItemType.find_by_name(
                        fb_so_item.typeObj.name
                    ).id,
                )
                session.add(sales_order_item)
                session.commit()
                backend_logger.debug(f"Creating sales order item {sales_order_item}.")

            if fb_parent_part in child_parts:
                fb_child_parts = child_parts[fb_parent_part]
            else:
                backend_logger.debug(f"Pulling child parts for {fb_parent_part.number}.")
                child_parts[fb_parent_part] = fb_child_parts = fb_utilities.get_child_parts(fishbowl_orm, fb_parent_part)
            
            prosess_child_fishbowl_parts(session, sales_order, sales_order_item, fb_so_item, fb_child_parts, part)


def prosess_child_fishbowl_parts(session: session_type_hint, sales_order: SalesOrder, sales_order_item: SalesOrderItem, fb_so_item: fb_models.FBSalesOrderItem, fb_child_parts: list[fb_models.FBPart], parent_part: Part):
    for index, fb_child_part in enumerate(fb_child_parts):
        backend_logger.debug(f"Processing child part {fb_child_part}.")
        child_part = Part.find_by_number(fb_child_part.number)
        if child_part is None:
            child_part = Part.from_fishbowl_part(fb_child_part)
            child_part.set_parent(parent_part)

        line_number = f"{fb_so_item.lineItem}.{index + 1}"
        child_sales_order_item = SalesOrderItem.find_by_fishbowl_so_item_id_line_number(fb_so_item.id, line_number)

        if child_sales_order_item is None and not child_part.excluded_from_import: # This keeps excluded parts from being imported.
            child_sales_order_item = SalesOrderItem(
                part_id=child_part.id,
                sales_order_id=sales_order.id,
                date_scheduled_fulfillment=fb_so_item.dateScheduledFulfillment,
                description=fb_so_item.description,
                fb_so_item_id=fb_so_item.id,
                quantity_fulfilled=fb_so_item.quantityFulfilled,
                quantity_ordered=fb_so_item.quantityOrdered,
                quantity_picked=fb_so_item.quantityPicked,
                quantity_to_fulfill=fb_so_item.quantityToFulfill,
                line_number=line_number,
                parent_item_id=sales_order_item.id,
                status_id=SalesOrderItemStatus.find_by_name(
                    fb_so_item.statusObj.name
                ).id,
                type_id=SalesOrderItemType.find_by_name(
                    fb_so_item.typeObj.name
                ).id,
            )
            session.add(child_sales_order_item)
            session.commit()
            backend_logger.debug(f"Creating child sales order item {child_sales_order_item}.")

# This line restarts the black magic.
# fmt: on


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


def pad_string(string: str, length: int, pad_char: str = " ") -> str:
    """Pad a string to a certain length."""
    return string.rjust(length, pad_char)

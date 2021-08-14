import os

from .database.fishbowldatabase import FishbowlDatabaseConnection
from .database.cutlistdatabase import CutListDatabase
from .appdataclasses.product import Product
from .appdataclasses.salesorder import SalesOrder, SalesOrderItem
from .appdataclasses.systemproperty import SystemProperty
from .logging import FileLogger


logger = FileLogger(__name__)

def touch(path):
    """This is the python equivalent of touch. It creates the file if it doesn't exist and updates the timestamp."""

    with open(path, 'a'):
        os.utime(path, None)

def add(cut_list_database,
        current_fishbowl_sales_order,
        fishbowl_product,
        fishbowl_line_number,
        fishbowl_due_date,
        fishbowl_qty_to_fulfill,
        fishbowl_qty_picked,
        fishbowl_qty_fulfilled,
        fishbowl_child_part_qty_multiple):
        
    item_in_order = False
    for current_item in current_fishbowl_sales_order.order_items:
        if current_item.product.number == fishbowl_product.number and current_item.line_number == fishbowl_line_number:
            item_in_order = True
            break

    if not item_in_order:
        order_item = SalesOrderItem(database_connection=cut_list_database,
                                    product=fishbowl_product,
                                    due_date=fishbowl_due_date,
                                    qty_to_fulfill=float(fishbowl_qty_to_fulfill) * fishbowl_child_part_qty_multiple,
                                    qty_picked=float(fishbowl_qty_picked) * fishbowl_child_part_qty_multiple,
                                    qty_fulfilled=float(fishbowl_qty_fulfilled) * fishbowl_child_part_qty_multiple,
                                    line_number=fishbowl_line_number,
                                    sales_order_id=current_fishbowl_sales_order.id)
        order_item.save()
        return 1
    return 0

def update_sales_order_data_from_fishbowl(fishbowl_database: FishbowlDatabaseConnection, cut_list_database: CutListDatabase):
    # TODO: Add ability to update sales order from fishbowl.

    logger.info("Updating sales order data from fishbowl.")

    fishbowl_data = fishbowl_database.get_all_open_sales_order_items()

    rows_inserted = 0
    rows_updated = 0
    total_rows = len(fishbowl_data)
    products_to_skip = SystemProperty.find_by_name(database_connection=cut_list_database, name="exclude_sales_order_products_starting_with").value

    for row in fishbowl_data:
        fishbowl_so_number = row['so_number']
        fishbowl_customer_name = row['customer_name']
        fishbowl_unit_price_dollars = row['unit_price_dollars']
        fishbowl_due_date = row['due_date']
        fishbowl_line_number = row['line_number']
        fishbowl_product_number = row['product_number']
        fishbowl_product_description = row['description']
        fishbowl_qty_to_fulfill = row['qty_to_fulfill']
        fishbowl_qty_picked = row['qty_picked']
        fishbowl_qty_fulfilled = row['qty_fulfilled']
        fishbowl_product_uom = row['uom']
        fishbowl_product = Product.from_number(database_connection=cut_list_database, number=fishbowl_product_number)
        fishbowl_child_parts = fishbowl_database.get_kit_items_for_product_number(fishbowl_product_number)
        fishbowl_child_part_qty_multiple = 1.0
        current_fishbowl_sales_order = SalesOrder.find_by_number(database_connection=cut_list_database, number=fishbowl_so_number)
        to_skip = False

        # Check if the product is in the exclude list.
        # TODO: Find a better way to do this?
        for item in products_to_skip:
            if fishbowl_product_number.startswith(item):
                logger.info(f"Skipping product number: {fishbowl_product_number}")
                to_skip = True
                break
        
        # If the product is in the exclude list, skip it.
        if to_skip:
            continue

        if not current_fishbowl_sales_order:
            current_fishbowl_sales_order = SalesOrder(database_connection=cut_list_database,
                                                        customer_name=fishbowl_customer_name,
                                                        number=fishbowl_so_number)
            current_fishbowl_sales_order.save()

        # Create and save parent product.
        if not fishbowl_product:
            fishbowl_product = Product(database_connection=cut_list_database,
                                    number=fishbowl_product_number,
                                    description=fishbowl_product_description,
                                    uom=fishbowl_product_uom,
                                    unit_price_dollars=fishbowl_unit_price_dollars)
            fishbowl_product.save()

        # Create and save child products if any.
        for child_part_data in fishbowl_child_parts:
            child_part = Product.from_number(database_connection=cut_list_database, number=child_part_data['child_part_number'])
            if not child_part:
                data = FishbowlDatabaseConnection.get_product_data_from_number(fishbowl_database, child_part_data['child_part_number'])
                child_product_description = data['description']
                child_product_uom = data['uom']
                child_unit_price_dollars = data['unit_price_dollars']
                fishbowl_child_part_qty_multiple = float(child_part_data['child_part_quantity'])

                child_part = Product(database_connection=cut_list_database,
                                    number=child_part_data['child_part_number'],
                                    description=child_product_description,
                                    uom=child_product_uom,
                                    unit_price_dollars=child_unit_price_dollars,
                                    kit_flag=True,
                                    parent_kit_product=fishbowl_product)
                child_part.save()

            rows_inserted += add(cut_list_database,
                        current_fishbowl_sales_order,
                        child_part,
                        fishbowl_line_number,
                        fishbowl_due_date,
                        fishbowl_qty_to_fulfill,
                        fishbowl_qty_picked,
                        fishbowl_qty_fulfilled,
                        fishbowl_child_part_qty_multiple)


        rows_inserted += add(cut_list_database,
                current_fishbowl_sales_order,
                fishbowl_product,
                fishbowl_line_number,
                fishbowl_due_date,
                fishbowl_qty_to_fulfill,
                fishbowl_qty_picked,
                fishbowl_qty_fulfilled,
                fishbowl_child_part_qty_multiple)

    logger.info(f"{rows_inserted} rows inserted from a total of {total_rows} rows.")
    return total_rows, rows_inserted


def create_default_system_properties(database_connection: CutListDatabase):
    logger.info("[SYSTEM PROPERTY] Creating default system properties.")

    if not SystemProperty.find_by_name(database_connection=database_connection, name="list_to_string_delimiter"):
        logger.info("[SYSTEM PROPERTY] Adding default system property 'list_to_string_delimiter'.")
        SystemProperty(database_connection=database_connection,
                        name="list_to_string_delimiter",
                        value=", ",
                        read_only=True,
                        visible=True).save()

    if not SystemProperty.find_by_name(database_connection=database_connection, name="fishbowl_auto_update_sales_orders"):
        logger.info("[SYSTEM PROPERTY] Adding default system property 'fishbowl_auto_update_sales_orders'.")
        SystemProperty(database_connection=database_connection,
                        name="fishbowl_auto_update_sales_orders",
                        value=True,
                        visible=True).save()
    
    if not SystemProperty.find_by_name(database_connection=database_connection, name="add_parent_products_to_sales_orders"):
        logger.info("[SYSTEM PROPERTY] Adding default system property 'add_parent_products_to_sales_orders'.")
        SystemProperty(database_connection=database_connection,
                        name="add_parent_products_to_sales_orders",
                        value=False,
                        visible=True).save()
    
    if not SystemProperty.find_by_name(database_connection=database_connection, name="exclude_sales_order_products_starting_with"):
        logger.info("[SYSTEM PROPERTY] Adding default system property 'exclude_sales_order_products_starting_with'.")
        SystemProperty(database_connection=database_connection,
                        name="exclude_sales_order_products_starting_with",
                        value=["BC-"],
                        visible=True).save()
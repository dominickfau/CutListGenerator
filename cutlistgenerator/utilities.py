import os, json, decimal, datetime
from typing import List, Tuple
from json import JSONEncoder

from .database.fishbowldatabase import FishbowlDatabaseConnection
from .database.cutlistdatabase import CutListDatabase
from .appdataclasses.product import Product
from .appdataclasses.salesorder import SalesOrder, SalesOrderItem
from .appdataclasses.systemproperty import SystemProperty
from .logging import FileLogger


logger = FileLogger(__name__)


class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
            return o.isoformat()
        to_return =  o.__dict__
        to_return.pop('database_connection', None)
        return to_return


def touch(path):
    """This is the python equivalent of touch. It creates the file if it doesn't exist and updates the timestamp."""

    with open(path, 'a'):
        os.utime(path, None)

def find_sales_order_item(database_connection: CutListDatabase, product_number: str, line_number: int, sales_order_number: str) -> Tuple[bool, SalesOrderItem]:
    values = {
        "product_number": product_number,
        "line_number": line_number,
        "sales_order_number": sales_order_number
    }

    cursor = database_connection.get_cursor()
    cursor.execute("""SELECT sales_order_item.*
                        FROM sales_order
                        JOIN sales_order_item ON sales_order_item.sales_order_id = sales_order.id
                        JOIN product ON sales_order_item.product_id = product.id
                        WHERE product.number = %(product_number)s
                        AND sales_order_item.line_number = %(line_number)s
                        AND sales_order.number = %(sales_order_number)s;""", values)
    data = cursor.fetchone()
    if not data:
        return False, None
    
    sales_order_item_id = data['id']
    sales_order_item = SalesOrderItem.from_id(database_connection, sales_order_item_id)
    return True, sales_order_item

def create_child_product_recursively(fishbowl_database_connection: FishbowlDatabaseConnection, parent_product: Product, child_product_number: str) -> None:
    """Creates a child products recursively."""
    child_product = Product.from_number(parent_product.database_connection, child_product_number)
    if not child_product:
        child_product_data = fishbowl_database_connection.get_product_data_from_number(child_product_number)
        child_product = Product(parent_product.database_connection, **child_product_data)

    child_product.set_parent_kit_product(parent_product)
    child_product.save()
    data = fishbowl_database_connection.get_child_products_for_product_number(child_product.number)
    for item in data:
        new_child_product_number = item['kit_part_number']
        create_child_product_recursively(fishbowl_database_connection, child_product, new_child_product_number)

def add_child_product_recursively(fishbowl_database_connection: FishbowlDatabaseConnection,
                                  cut_list_database: CutListDatabase,
                                  parent_sales_order: SalesOrder,
                                  parent_sales_order_item: SalesOrderItem,
                                  child_product_number: str) -> None:
    """Adds child products recursively to a sales order."""
    global total_rows
    global rows_inserted
    global rows_updated

    child_product = Product.from_number(cut_list_database, child_product_number)
    # TODO: Add ability to check if this child product should be added to the sales order.
    if child_product:
        values = {
            'product': child_product,
            'due_date': parent_sales_order_item.due_date,
            'qty_to_fulfill': parent_sales_order_item.qty_to_fulfill,
            'qty_picked': parent_sales_order_item.qty_picked,
            'qty_fulfilled': parent_sales_order_item.qty_fulfilled,
            'line_number': parent_sales_order_item.line_number,
            'sales_order_id': parent_sales_order.id
        }

        logger.debug(f"[RECURSIVE SO ITEM] Checking if child product {child_product_number} is already in the sales order.")
        found, sales_order_item = find_sales_order_item(cut_list_database,
                                                        child_product.number,
                                                        parent_sales_order_item.line_number,
                                                        parent_sales_order.number)
        if not found:
            logger.debug("[RECURSIVE SO ITEM] Adding child product to the sales order.")
            sales_order_item = SalesOrderItem(database_connection=cut_list_database, **values)
            parent_sales_order.add_item(sales_order_item)
            rows_inserted += 1
        else:
            logger.debug("[RECURSIVE SO ITEM] Child product already in the sales order.")
            rows_updated += 1
            
        logger.info(f"[RECURSIVE SO ITEM] Looking for child products for {child_product_number}.")
        data = fishbowl_database_connection.get_child_products_for_product_number(child_product.number)
        for item in data:
            new_child_product_number = item['kit_part_number']
            add_child_product_recursively(fishbowl_database_connection,
                                          cut_list_database,
                                          parent_sales_order,
                                          parent_sales_order_item,
                                          new_child_product_number)
            total_rows += 1

def update_sales_order_data_from_fishbowl(fishbowl_database_connection_parameters: dict,
                                          cut_list_database: CutListDatabase,
                                          progress_signal = None,
                                          progress_data_signal = None):
    # TODO: Add ability to update sales order from fishbowl.

    # FIXME: Find a more efficient way to do this.

    update_time_start = datetime.datetime.now()

    logger.info("Updating sales order data from fishbowl.")
    add_parent_products = SystemProperty.find_by_name(database_connection=cut_list_database, name="add_parent_products_to_sales_orders").value
    logger.debug(f"[SYSTEM PROPERTY] add_parent_products_to_sales_orders = {add_parent_products}")
    products_to_skip = SystemProperty.find_by_name(database_connection=cut_list_database, name="exclude_sales_order_products_starting_with").value
    logger.debug(f"[SYSTEM PROPERTY] products_to_skip = {products_to_skip}")

    logger.info("Connecting to fishbowl database.")
    fishbowl_database = FishbowlDatabaseConnection(fishbowl_database_connection_parameters)

    fishbowl_data = fishbowl_database.get_all_open_sales_order_items()

    global total_rows
    global rows_inserted
    global rows_updated
    rows_inserted = 0
    rows_updated = 0
    total_rows = len(fishbowl_data)

    if len(fishbowl_data) == 0:
        logger.info("No open sales orders found in fishbowl database.")
        return
    logger.info(f"Found {len(fishbowl_data)} open sales orders in fishbowl database.")

    
    logger.info("Creating sales order objects for all open sales orders in fishbowl.")
    fishbowl_sales_orders = {}
    for index, row in enumerate(fishbowl_data, start=1):
        if progress_signal:
            progress_signal.emit(index / total_rows * 100)

        row_processing_time_start = datetime.datetime.now()

        logger.debug(f"[NEXT SALES ORDER ITEM] Processing row {index} of {total_rows}.")
        so_number = row['so_number']
        customer_name = row['customer_name']

        logger.debug(f"On Fishbowl sales order {so_number}.")
        if progress_data_signal:
            progress_data_signal.emit(f"Processing sales order: {so_number}")

        sales_order_data = {
            'customer_name': customer_name,
            'number': so_number
        }
        if so_number not in fishbowl_sales_orders:
            logger.debug("Looking for a matching sales order in the database.")
            sales_order = SalesOrder.find_by_number(cut_list_database, so_number)
            if sales_order is None:
                logger.debug("Sales order not found in database. Creating a new one.")
                sales_order = SalesOrder(database_connection=cut_list_database, **sales_order_data)
            else:
                logger.debug("Sales order found in database. Updating it.")
        else:
            logger.debug("Updating existing sales order object.")
            sales_order = fishbowl_sales_orders[so_number]

        product_number = row['product_number']
        description = row['description']
        uom = row['uom']
        unit_price_dollars = row['unit_price_dollars']
        product_data = {
            'number': product_number,
            'description': description,
            'uom': uom,
            'unit_price_dollars': unit_price_dollars
        }
        
        logger.debug(f"Looking for product number {product_number} in the database.")
        product = Product.from_number(cut_list_database, product_number)
        if product is None:
            logger.debug("Product not found in database. Creating a new one.")
            product = Product(database_connection=cut_list_database, **product_data)
            product.save()
            child_data = fishbowl_database.get_child_products_for_product_number(product_number)
            for child_row in child_data:
                child_product_number = child_row['kit_part_number']
                create_child_product_recursively(fishbowl_database, product, child_product_number)
        else:
            logger.debug("Product found in database. Updating it.")

        # # Check if the product is in the exclude list.
        # # TODO: Find a better way to do this?
        # to_skip = False
        # for item in products_to_skip:
        #     if product.number.startswith(item):
        #         logger.info(f"Skipping product number: {product.number}")
        #         to_skip = True
        #         break
        
        # # If the product is in the exclude list, skip it.
        # if to_skip:
        #     continue

        line_number = row['line_number']
        due_date = row['due_date']
        qty_to_fulfill = row['qty_to_fulfill']
        qty_picked = row['qty_picked']
        qty_fulfilled = row['qty_fulfilled']

        sales_order_item_data = {
            'product': product,
            'due_date': due_date,
            'qty_to_fulfill': qty_to_fulfill,
            'qty_picked': qty_picked,
            'qty_fulfilled': qty_fulfilled,
            'line_number': line_number
        }

        logger.debug(f"Looking for sales order item with SO Number: {so_number} Product Number: {product_number} and Line Number: {line_number} in the database.")
        found, sales_order_item = find_sales_order_item(cut_list_database, product_number, line_number, so_number)
        if not found:
            logger.debug("Sales order item not found in database. Creating a new one.")
            sales_order_item = SalesOrderItem(database_connection=cut_list_database, **sales_order_item_data)
            sales_order.add_item(sales_order_item)
            rows_inserted += 1
            logger.info(f"Looking for all child products for product number {product.number} to add to the sales order.")
            child_products = fishbowl_database.get_child_products_for_product_number(product.number)
            for child_row in child_products:
                child_product_number = child_row['kit_part_number']
                add_child_product_recursively(fishbowl_database,
                                            cut_list_database,
                                            parent_sales_order=sales_order,
                                            parent_sales_order_item=sales_order_item,
                                            child_product_number=child_product_number)
                total_rows += 1
        else:
            # TODO: Code to update the sales order item.
            logger.debug("Sales order item found in database. Updating it.")
            rows_updated += 1

        logger.debug("Finished processing row.")
        logger.info(f"Row processing time: {(datetime.datetime.now() - row_processing_time_start).total_seconds()} seconds.")
        fishbowl_sales_orders[so_number] = sales_order

    logger.info("Finished processing all open sales orders in fishbowl.")
    logger.info("Saving sales order objects to the database.")
    logger.info(f"Total row processing time: {(datetime.datetime.now() - update_time_start).total_seconds()} seconds.")

    save_start_time = datetime.datetime.now()

    # Reset progress bar to 0.
    if progress_signal:
        progress_signal.emit(0)

    if progress_data_signal:
        progress_data_signal.emit("Saving sales orders.")

    for index, so_number in enumerate(fishbowl_sales_orders, start=1):
        if progress_data_signal:
            progress_data_signal.emit(f"Saving sales order: {so_number}. {index} of {len(fishbowl_sales_orders)}.")

        if progress_signal:
            progress_signal.emit(index / total_rows * 100)
        logger.debug(f"Saving sales order {so_number}.")
        sales_order = fishbowl_sales_orders[so_number]
        sales_order.save()
    logger.info("Finished saving all sales orders in fishbowl.")
    logger.info(f"Total save time: {(datetime.datetime.now() - save_start_time).total_seconds()} seconds.")

    logger.info(f"{rows_inserted} rows inserted from a total of {total_rows} rows.")
    logger.info(f"Total run time: {(datetime.datetime.now() - update_time_start).total_seconds()} seconds.")
    return total_rows, rows_inserted


def create_default_system_properties(database_connection: CutListDatabase):
    logger.info("[SYSTEM PROPERTY] Checking that all system properties exist.")

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
                        value=False,
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
    
    if not SystemProperty.find_by_name(database_connection=database_connection, name="date_formate"):
        logger.info("[SYSTEM PROPERTY] Adding default system property 'date_formate'.")
        SystemProperty(database_connection=database_connection,
                        name="date_formate",
                        value="%m-%d-%Y %I:%M %p",
                        visible=True).save()
    
    logger.info("[SYSTEM PROPERTY] Finished. All system properties should now exist.")

def create_database(database_connection: CutListDatabase):
    database_connection.create()
    logger.info("[DATABASE] Adding default data to tables.")
    create_default_system_properties(database_connection)

def convert_string_to_pixel_width(string_width: str) -> int:
    """Convert a string to a pixel width."""
    # TODO: Create a function to do this.
    pass

def get_table_headers(table_widget) -> dict:
    """Returns a dict of the headers for the given table widget."""
    headers = {}
    for index in range(table_widget.columnCount()):
        header = table_widget.horizontalHeaderItem(index)
        if header is not None:
            header_name = header.text()
            width = len(header_name) * len(header_name) / 2
            width = int(width)
            headers[header_name] = {'index': index, 'width': width}
    return headers

def get_max_column_widths(table_data: List[dict], table_headers: dict) -> int:
    """Returns the maximum width for each column."""
    max_column_widths = table_headers

    # for column_name, column_data in table_headers.items():
    #     for row_data in table_data:
    #         if column_name in row_data:
    #             cell_type = type(row_data[column_name])
    #             cell_value = str(row_data[column_name])
    #             cell_legnth = len(cell_value) * 10
    #             if cell_legnth > max_column_widths[column_name]['width']:
    #                 max_column_widths[column_name]['width'] = cell_legnth
    return max_column_widths
from cutlistgenerator.database import FishbowlDatabase, CutListDatabase
from cutlistgenerator.appdataclasses import Product, SalesOrder, SalesOrderItem
import datetime


def update_sales_order_data_from_fishbowl(fishbowl_database: FishbowlDatabase, cut_list_database: CutListDatabase):
    # TODO: Implement parent_kit_product_number.
    start_time = datetime.datetime.now()
    fishbowl_data = fishbowl_database.get_all_open_sales_order_items()

    rows_inserted = 0
    rows_updated = 0
    total_rows = len(fishbowl_data)

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
        print(f"On SO: {fishbowl_so_number}, Row Number: {rows_inserted}")

        if not fishbowl_product:
            fishbowl_product = Product(database_connection=cut_list_database,
                                    number=fishbowl_product_number,
                                    description=fishbowl_product_description,
                                    uom=fishbowl_product_uom,
                                    unit_price_dollars=fishbowl_unit_price_dollars,
                                    kit_flag=False,
                                    parent_kit_product=None)
            fishbowl_product.save()

        current_fishbowl_sales_order = SalesOrder.find_by_number(database_connection=cut_list_database, number=fishbowl_so_number)

        if not current_fishbowl_sales_order:
            current_fishbowl_sales_order = SalesOrder(database_connection=cut_list_database,
                                                        customer_name=fishbowl_customer_name,
                                                        number=fishbowl_so_number)
            current_fishbowl_sales_order.save()
        
        # TODO: Add ability to update sales order from fishbowl.


        if len(current_fishbowl_sales_order.order_items) == 0:
            order_item = SalesOrderItem(database_connection=cut_list_database,
                                        product=fishbowl_product,
                                        due_date=fishbowl_due_date,
                                        qty_to_fulfill=fishbowl_qty_to_fulfill,
                                        qty_picked=fishbowl_qty_picked,
                                        qty_fulfilled=fishbowl_qty_fulfilled,
                                        line_number=fishbowl_line_number,
                                        sales_order_id=current_fishbowl_sales_order.id)
            order_item.save()
            rows_inserted += 1
            continue

        item_in_order = False
        for current_item in current_fishbowl_sales_order.order_items:
            if current_item.product.number == fishbowl_product.number and current_item.line_number == fishbowl_line_number:
                item_in_order = True
                break

        if not item_in_order:
            order_item = SalesOrderItem(database_connection=cut_list_database,
                                        product=fishbowl_product,
                                        due_date=fishbowl_due_date,
                                        qty_to_fulfill=fishbowl_qty_to_fulfill,
                                        qty_picked=fishbowl_qty_picked,
                                        qty_fulfilled=fishbowl_qty_fulfilled,
                                        line_number=fishbowl_line_number,
                                        sales_order_id=current_fishbowl_sales_order.id)
            order_item.save()
            rows_inserted += 1
    
    end_time = datetime.datetime.now()

    print(f"Total time: {end_time - start_time}")
    
    return total_rows, rows_inserted
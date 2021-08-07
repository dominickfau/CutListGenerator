from cutlistgenerator.database import FishbowlDatabase, CutListDatabase
from cutlistgenerator.appdataclasses import Product, SalesOrder, SalesOrderItem


def update_sales_order_data_from_fishbowl(fishbowl_database: FishbowlDatabase, cut_list_database: CutListDatabase):
    fishbowl_data = fishbowl_database.get_all_open_sales_order_items()

    # Keys in fishbowl_data.
    # so_number, customer_name, due_date, line_number, product_number, description, qty_to_fulfill, qty_picked, qty_fulfilled, uom

    rows_inserted = 0
    rows_updated = 0
    total_rows = len(fishbowl_data)

    for row in fishbowl_data:
        so_number = row['so_number']
        current_sales_order = SalesOrder.find_by_number(cut_list_database, number=so_number)
        current_product_number = row['product_number']
        current_line_number = row['line_number']
        current_product_description = row['description']
        current_product_uom = row['uom']
        current_product_unit_price_dollars = row['unit_price_dollars']


        current_product = Product.from_number(database_connection=cut_list_database, number=current_product_number)

        if not current_product:
            # TODO: Add parent kit product.
            current_product = Product(database_connection=cut_list_database,
                                    number=current_product_number,
                                    description=current_product_description,
                                    uom=current_product_uom,
                                    unit_price_dollars=current_product_unit_price_dollars,
                                    kit_flag=False,
                                    parent_kit_product=None)
        current_product.save()
        
        if current_sales_order:
            # TODO: Add ability to update sales order from fishbowl.
            
            for current_item in current_sales_order.order_items:
                if current_item.product.number == current_product.number and current_item.line_number == current_line_number:
                    continue
                
                order_item = SalesOrderItem(database_connection=cut_list_database,
                                            product=current_product,
                                            due_date=row['due_date'],
                                            qty_to_fulfill=row['qty_to_fulfill'],
                                            qty_picked=row['qty_picked'],
                                            qty_fulfilled=row['qty_fulfilled'],
                                            line_number=current_line_number,
                                            sales_order_id=current_sales_order.id)
                current_sales_order.add_item(order_item)
                current_sales_order.save()
        else:
            current_sales_order = SalesOrder(database_connection=cut_list_database,
                                                customer_name=row['customer_name'],
                                                number=so_number)
            current_sales_order.save()
            
            order_item = SalesOrderItem(database_connection=cut_list_database,
                                            product=current_product,
                                            due_date=row['due_date'],
                                            qty_to_fulfill=row['qty_to_fulfill'],
                                            qty_picked=row['qty_picked'],
                                            qty_fulfilled=row['qty_fulfilled'],
                                            line_number=current_line_number,
                                            sales_order_id=current_sales_order.id)
            current_sales_order.add_item(order_item)
            current_sales_order.save()

        rows_inserted += 1
    
    return total_rows, rows_inserted
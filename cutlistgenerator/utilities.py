from cutlistgenerator.database import FishbowlDatabase, CutListDatabase
from cutlistgenerator.appdataclasses import SalesOrder


def update_sales_order_data_from_fishbowl(fishbowl_database: FishbowlDatabase, cut_list_database: CutListDatabase):
    fishbowl_cursor = fishbowl_database.__get_cursor()

    fishbowl_data = fishbowl_database.get_all_open_sales_order_items()

    # Keys in fishbowl_data.
    # so_number, customer_name, due_date, line_number, product_number, description, qty_to_fulfill, qty_picked, qty_fulfilled, uom

    rows_inserted = 0
    rows_updated = 0
    total_rows = len(fishbowl_data)

    for row in fishbowl_data:
        so_number = row['so_number']
        current_sales_order = SalesOrder.find_by_number(cut_list_database, number=so_number)
        
        if current_sales_order:
            # Update the current sales order items with the data from the fishbowl.
            for order_item in current_sales_order.order_items:
                if order_item.product.number != row['product_number'] and order_item.line_number != row['line_number']:
                    continue
                
                order_item.due_date = row['due_date']
                order_item.qty_picked = row['qty_picked']
                order_item.qty_fulfilled = row['qty_fulfilled']
                order_item.qty_to_fulfill = row['qty_to_fulfill']
                order_item.product.description = row['description']
                order_item.product.uom = row['uom']
                order_item.product.unit_price_dollars = row['unit_price_dollars']
        


            
        
    
        rows_inserted += 1
    
    fishbowl_cursor.close()
from . import *

from .cutlistdatabase import CutListDatabase
from cutlistgenerator.logging import FileLogger
# from .mysqldatabasecreate import TABLE_DATA

logger = FileLogger(__name__)

class MySQLDatabaseConnection(CutListDatabase):
    """MySQL Database Connection for the cut list database."""

    # TODO: Check if all methods below are apart of the CutListDatabase interface.

    def connect(self):
        self.connection = mysql.connector.connect(**self.connection_args)

    def get_cursor(self, buffered=None, raw=None, prepared=None, cursor_class=None, dictionary=True, named_tuple=None):
        """Get a cursor to the database. Defaults to a dictionary cursor."""
        if not self.connection:
            self.connect()

        return self.connection.cursor(buffered, raw, prepared, cursor_class, dictionary, named_tuple)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create(self, force_remove_old_data: bool = False) -> None:
        """Create the database"""
        pass
        # logger.info("[DATABASE] Creating database.")
        # cursor = self.get_cursor(dictionary=False)
        # # cursor.execute("SELECT database() AS selected_database;")
        # # selected_database = cursor.fetchone()['selected_database']

        # cursor.execute("SHOW tables;")
        # tables = [table for (table,) in cursor.fetchall()]
        # logger.info(f"[DATABASE] Current tables: {tables}")

        # if force_remove_old_data:
        #     logger.warning("[DATABASE] Forcing removal of old tables. Any data in the database will be lost.")

        #     for table in tables:
        #         logger.debug(f"[DATABASE] Dropping table {table}.")
        #         cursor.execute(f"DROP TABLE {table};")
        #         cursor.execute("COMMIT;")

        # logger.info("[DATABASE] Creating tables.")
        # for table in TABLE_DATA:
        #     if table not in tables:
        #         logger.debug(f"[DATABASE] Creating table: {table}")
        #         cursor.execute(TABLE_DATA[table]['create'])
        #         cursor.execute("COMMIT;")
        
        # logger.info(f"[DATABASE] All tables created. Total: {len(TABLE_DATA)}")
        # logger.info("[DATABASE] Database created.")


    def get_current_version(self) -> dict:
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM database_version ORDER BY id DESC LIMIT 1")
        return cursor.fetchone()
    
    def get_product_by_number(self, number: str) -> dict:
        cursor = self.get_cursor()
        values = {
            'number': number
        }

        cursor.execute("SELECT * FROM product WHERE number = %(number)s", values)
        product = cursor.fetchone()
        cursor.close()
        if not product:
            return None
        return product
    
    def get_product_by_id(self, id: int) -> dict:
        cursor = self.get_cursor()
        values = {
            'id': id
        }

        cursor.execute("SELECT * FROM product WHERE id = %(id)s", values)
        product = cursor.fetchone()
        cursor.close()
        if not product:
            return None
        return product
    
    def get_all_products(self) -> List[dict]:
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM product ORDER BY number")
        products = cursor.fetchall()
        cursor.close()
        if not products:
            return []
        return products
    
    def save_product_relationship(self, parent_product_id: int, child_product_id: int) -> None:
        values = {
            'child_product_id': child_product_id,
            'parent_product_id': parent_product_id
        }
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM parent_to_child_product WHERE parent_product_id = %(parent_product_id)s AND child_product_id = %(child_product_id)s", values)
        data = cursor.fetchone()
        if not data:
            cursor.execute("INSERT INTO parent_to_child_product (child_product_id, parent_product_id) VALUES (%(child_product_id)s, %(parent_product_id)s)", values)
        cursor.execute("COMMIT;")
        cursor.close()
    
    def remove_product_relationship(self, parent_product_id: int, child_product_id: int) -> None:
        values = {
            'child_product_id': child_product_id,
            'parent_product_id': parent_product_id
        }
        cursor = self.get_cursor()
        cursor.execute("DELETE FROM parent_to_child_product WHERE child_product_id = %(child_product_id)s AND parent_product_id = %(parent_product_id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()

    def save_product(self, product) -> int:
        values = {
            'number': product.number,
            'description': product.description,
            'uom': product.uom,
            'unit_price_dollars': product.unit_price_dollars,
            'kit_flag': product.kit_flag,
            'id': product.id
        }

        cursor = self.get_cursor()

        if product.id is None:
            cursor.execute("""INSERT INTO product (number, description, uom, unit_price_dollars, kit_flag)
                                VALUES(%(number)s, %(description)s, %(uom)s, %(unit_price_dollars)s, %(kit_flag)s)""", values)
            product_id = cursor.lastrowid
            values['id'] = product_id
        else:
            cursor.execute("""UPDATE product SET number = %(number)s, description = %(description)s, uom = %(uom)s,
                                unit_price_dollars = %(unit_price_dollars)s, kit_flag = %(kit_flag)s
                                WHERE id = %(id)s""", values)
            product_id = values["id"]

        cursor.execute("COMMIT;")
        cursor.close()
        return product_id
    
    def delete_product(self, product) -> None:
        values = {
            'id': product.id
        }

        cursor = self.get_cursor()
        cursor.execute("DELETE FROM product WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()
    
    def get_child_products_from_parent_product_id(self, parent_product_id) -> List[dict]:
        values = {
            'parent_product_id': parent_product_id
        }

        cursor = self.get_cursor()
        cursor.execute("""SELECT DISTINCT product.*
                        FROM parent_to_child_product
                        JOIN product ON parent_to_child_product.child_product_id = product.id
                        WHERE parent_product_id = %(parent_product_id)s""", values) 
        parent_product = cursor.fetchall()
        cursor.close()
        if not parent_product:
            return []
        return parent_product

    
    # WireCutterOptions methods
    def get_wire_cutter_option_by_id(self, wire_cutter_option_id: int) -> dict:
        values = {
            'id': wire_cutter_option_id
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM wire_cutter_option WHERE id = %(id)s", values)
        wire_cutter_option = cursor.fetchone()
        cursor.close()
        if not wire_cutter_option:
            return None
        return wire_cutter_option
    
    def get_wire_cutter_option_by_name(self, wire_cutter_option_name: int) -> dict:
        values = {
            'name': wire_cutter_option_name
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM wire_cutter_option WHERE name = %(name)s", values)
        wire_cutter_option = cursor.fetchone()
        cursor.close()
        if not wire_cutter_option:
            return None
        return wire_cutter_option
    
    def get_wire_cutter_options_by_wire_cutter_id(self, wire_cutter_id: int) -> List[dict]:
        values = {
            'wire_cutter_id': wire_cutter_id
        }

        cursor = self.get_cursor()
        cursor.execute("""
                SELECT wire_cutter_option.* FROM wire_cutter_option
                JOIN wire_cutter_to_wire_cutter_option ON wire_cutter_option.id = wire_cutter_to_wire_cutter_option.wire_cutter_option_id
                JOIN wire_cutter ON wire_cutter_to_wire_cutter_option.wire_cutter_id = wire_cutter.id
                WHERE wire_cutter.id = %(wire_cutter_id)s""", values)
        wire_cutter_options = cursor.fetchall()
        cursor.close()
        if not wire_cutter_options:
            return []
        return wire_cutter_options
    
    def get_wire_cutter_options_by_wire_cutter_name(self, wire_cutter_name: str) -> List[dict]:
        values = {
            'wire_cutter_name': wire_cutter_name
        }

        cursor = self.get_cursor()
        cursor.execute("""
                SELECT wire_cutter_option.* FROM wire_cutter_option
                JOIN wire_cutter_to_wire_cutter_option ON wire_cutter_option.id = wire_cutter_to_wire_cutter_option.wire_cutter_option_id
                JOIN wire_cutter ON wire_cutter_to_wire_cutter_option.wire_cutter_id = wire_cutter.id
                WHERE wire_cutter.name = %(wire_cutter_name)s""", values)
        wire_cutter_options = cursor.fetchall()
        cursor.close()
        if not wire_cutter_options:
            return []
        return wire_cutter_options
    
    def save_wire_cutter_option(self, wire_cutter_option) -> int:
        values = {
            'name': wire_cutter_option.name,
            'description': wire_cutter_option.description,
            'id': wire_cutter_option.id
        }

        cursor = self.get_cursor()
        if wire_cutter_option.id is None:
            cursor.execute("""INSERT INTO wire_cutter_option (name, descrition)
                                VALUES(%(name)s, %(description)s)""", values)
            wire_cutter_option_id = cursor.lastrowid
        else:
            cursor.execute("""UPDATE wire_cutter_option SET name = %(name)s, description = %(description)s
                                WHERE id = %(id)s""", values)
            wire_cutter_option_id = values["id"]
        cursor.execute("COMMIT;")
        cursor.close()
        return wire_cutter_option_id
    
    def delete_wire_cutter_option(self, wire_cutter_option) -> None:
        values = {
            'id': wire_cutter_option.id
        }

        cursor = self.get_cursor()
        cursor.execute("DELETE FROM wire_cutter_option WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()

    # WireCutter methods
    def get_wire_cutter_by_name(self, name: str) -> dict:
        values = {
            'name': name
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM wire_cutter WHERE name = %(name)s", values)
        wire_cutter = cursor.fetchone()
        cursor.close()
        if not wire_cutter:
            return None
        return wire_cutter
    
    def get_wire_cutter_by_id(self, wire_cutter_id: int) -> dict:
        values = {
            'id': wire_cutter_id
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM wire_cutter WHERE id = %(id)s", values)
        wire_cutter = cursor.fetchone()
        cursor.close()
        if not wire_cutter:
            return None
        return wire_cutter

    def get_all_wire_cutters(self) -> dict:
        """Gets a list of all wire cutters in the database. Along with any options."""
        wire_cutters = {}
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM wire_cutter")
        wire_cutter_data = cursor.fetchall()
        for wire_cutter in wire_cutter_data:
            wire_cutters[wire_cutter["name"]] = wire_cutter
            wire_cutter_name = wire_cutter["name"]
            wire_cutter_options = self.get_wire_cutter_options_by_wire_cutter_name(wire_cutter_name)
            wire_cutters[wire_cutter_name]["options"] = wire_cutter_options
        cursor.close()
        return wire_cutters

    def save_wire_cutter(self, wire_cutter) -> int:
        values = {
            'name': wire_cutter.name,
            'max_wire_gauge_awg': wire_cutter.max_wire_gauge_awg,
            'processing_speed_feet_per_minute': wire_cutter.processing_speed_feet_per_minute,
            'details': wire_cutter.details,
            'id': wire_cutter.id
        }
        cursor = self.get_cursor()

        # Save the wire_cutter
        if wire_cutter.id is None:
            cursor.execute("""INSERT INTO wire_cutter (name, max_wire_gauge_awg, processing_speed_feet_per_minute, details)
                                VALUES(%(name)s, %(max_wire_gauge_awg)s, %(processing_speed_feet_per_minute)s, %(details)s)""", values)
            wire_cutter_id = cursor.lastrowid
        else:
            cursor.execute("""UPDATE wire_cutter SET name = %(name)s, max_wire_gauge_awg = %(max_wire_gauge_awg)s, processing_speed_feet_per_minute = %(processing_speed_feet_per_minute)s, details = %(details)s
                                WHERE id = %(id)s""", values)
            wire_cutter_id = values["id"]
        
        # Save the wire_cutter_to_wire_cutter_option relationship
        for wire_cutter_option in wire_cutter.options:
            values = {
                'wire_cutter_id': wire_cutter_id,
                'wire_cutter_option_id': wire_cutter_option.id
            }

            # Query to see if the wire_cutter_to_wire_cutter_option relationship already exists
            cursor.execute("""
                SELECT * FROM wire_cutter_to_wire_cutter_option
                WHERE wire_cutter_id = %(wire_cutter_id)s
                AND wire_cutter_option_id = %(wire_cutter_option_id)s""", values)
            data = cursor.fetchone()
            if not data:
                cursor.execute("""INSERT INTO wire_cutter_to_wire_cutter_option (wire_cutter_id, wire_cutter_option_id)
                                    VALUES(%(wire_cutter_id)s, %(wire_cutter_option_id)s)""", values)
            else:
                values['id'] = data['id']
                cursor.execute("""
                    UPDATE wire_cutter_to_wire_cutter_option
                    SET wire_cutter_id = %(wire_cutter_id)s,
                    wire_cutter_option_id = %(wire_cutter_option_id)s
                    WHERE id = %(id)s""", values)

        cursor.execute("COMMIT;")
        cursor.close()
        return wire_cutter_id
    
    def delete_wire_cutter(self, wire_cutter) -> None:
        values = {
            'id': wire_cutter.id
        }

        cursor = self.get_cursor()
        cursor.execute("DELETE FROM wire_cutter WHERE id = %(id)s", values)

        # Delete the wire_cutter_to_wire_cutter_option relationship
        cursor.execute("""
            DELETE FROM wire_cutter_to_wire_cutter_option
            WHERE wire_cutter_id = %(id)s""", values)
        cursor.execute("COMMIT;")
        cursor.close()
    
    # Sales Order Item methods
    def get_sales_order_items_by_sales_order_id(self, sales_order_id: int) -> List[dict]:
        # TODO: Change query.
        values = {
            'sales_order_id': sales_order_id
        }

        cursor = self.get_cursor()
        cursor.execute("""SELECT * FROM sales_order_item
                            WHERE sales_order_id = %(sales_order_id)s""", values)
        items = cursor.fetchall()
        cursor.close()
        if not items:
            return []
        return items

    def get_sales_order_item_by_id(self, sales_order_item_id: int) -> dict:
        values = {
            'id': sales_order_item_id
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM sales_order_item WHERE id = %(id)s", values)
        sales_order_item = cursor.fetchone()
        cursor.close()
        if not sales_order_item:
            return None
        return sales_order_item

    def get_sales_order_item_by_product_and_line_number(self, product, line_number: int) -> List[dict]:
        # TODO: Change query.
        values = {
            'product_number': product.number,
            'line_number': line_number
        }

        cursor = self.get_cursor()
        cursor.execute("""
            SELECT sales_order_item.id AS so_item_id,
                sales_order_item.sales_order_id AS so_id,
                sales_order_item.due_date AS due_date,
                sales_order_item.qty_to_fulfill AS qty_to_fulfill,
                sales_order_item.qty_picked AS qty_picked,
                sales_order_item.qty_fulfilled AS qty_fulfilled,
                product.id AS product_id,
                product.number AS product_number,
                product.description AS product_description,
                product.uom AS uom,
                product.unit_price_dollars AS unit_price_dollars,
                product.kit_flag AS kit_flag,
                parent_to_child_product.parent_product_id AS parent_kit_product_id

            FROM sales_order_item
            JOIN product ON sales_order_item.product_id = product.id
            LEFT JOIN parent_to_child_product ON product.id = parent_to_child_product.child_product_id
            WHERE product.number = %(product_number)s
            AND sales_order_item.line_number = %(line_number)s""", values)
        sales_order_items = cursor.fetchall()
        cursor.close()
        if not sales_order_items:
            return None
        return sales_order_items
    
    def get_sales_order_items_by_sales_order_number(self, number: str) -> List[dict]:
        # TODO: Change query.
        values = {
            'number': number
        }

        cursor = self.get_cursor()
        cursor.execute("""
            SELECT sales_order_item.*
            FROM sales_order_item
            JOIN sales_order ON sales_order.id = sales_order_item.sales_order_id
            WHERE sales_order.number = %(number)s""", values)
        sales_order_items = cursor.fetchall()
        cursor.close()
        if not sales_order_items:
            return []
        return sales_order_items
    
    def save_sales_order_item(self, sales_order_item) -> int:
        values = {
            'sales_order_id': sales_order_item.sales_order_id,
            'due_date': sales_order_item.due_date,
            'product_id': sales_order_item.product.id,
            'qty_to_fulfill': sales_order_item.qty_to_fulfill,
            'qty_fulfilled': sales_order_item.qty_fulfilled,
            'qty_picked': sales_order_item.qty_picked,
            'line_number': sales_order_item.line_number,
            'id': sales_order_item.id,
            'cut_in_full': sales_order_item.cut_in_full
        }

        cursor = self.get_cursor()
        if sales_order_item.id is None:
            cursor.execute("""INSERT INTO sales_order_item (sales_order_id, due_date, product_id, qty_to_fulfill, qty_fulfilled, qty_picked, line_number, cut_in_full)
                                VALUES(%(sales_order_id)s, %(due_date)s, %(product_id)s, %(qty_to_fulfill)s, %(qty_fulfilled)s, %(qty_picked)s, %(line_number)s, %(cut_in_full)s)""", values)
            sales_order_item_id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE sales_order_item
                SET sales_order_id = %(sales_order_id)s,
                due_date = %(due_date)s,
                product_id = %(product_id)s,
                qty_to_fulfill = %(qty_to_fulfill)s,
                qty_fulfilled =  %(qty_fulfilled)s,
                qty_picked = %(qty_picked)s,
                line_number = %(line_number)s,
                cut_in_full = %(cut_in_full)s
                WHERE id = %(id)s""", values)
            sales_order_item_id = values["id"]
        cursor.execute("COMMIT;")
        cursor.close()
        return sales_order_item_id
        
    def delete_sales_order_item(self, sales_order_item) -> None:
        values = {
            'id': sales_order_item.id
        }

        cursor = self.get_cursor()
        cursor.execute("DELETE FROM sales_order_item WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()
    
    # Sales Order methods
    def get_sales_order_by_id(self, id: int) -> dict:
        values = {
            'id': id
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM sales_order WHERE id = %(id)s", values)
        sales_order = cursor.fetchone()
        cursor.close()
        if not sales_order:
            return None
        return sales_order

    def get_sales_order_by_number(self, number: str) -> dict:
        values = {
            'number': number
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM sales_order WHERE number = %(number)s", values)
        sales_order = cursor.fetchone()
        cursor.close()
        if not sales_order:
            return None
        return sales_order
    
    def get_sales_order_by_sales_order_item_id(self, sales_order_item_id: int) -> dict:
        values = {
            'sales_order_item_id': sales_order_item_id
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM sales_order_item WHERE id = %(sales_order_item_id)s", values)
        sales_order_items = cursor.fetchall()
        if not sales_order_items:
            return None
        sales_order_id = sales_order_items[0]["sales_order_id"]
        values = {
            'sales_order_id': sales_order_id
        }

        cursor.execute("SELECT * FROM sales_order WHERE id = %(sales_order_id)s", values)
        sales_order = cursor.fetchone()
        cursor.close()
        if not sales_order:
            return None
        return {
                    "sales_order": sales_order,
                    "sales_order_items": sales_order_items
                }

    def get_all_sales_orders(self) -> List[dict]:
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM sales_order")
        sales_orders = cursor.fetchall()
        cursor.close()
        if not sales_orders:
            return []
        return sales_orders
    
    def get_all_sales_orders_by_customer_name(self, customer_name: str) -> List[dict]:
        # TODO: Check how fast this is.
        all_orders = self.get_all_sales_orders()
        return [order for order in all_orders if order['customer_name'] == customer_name]
    
    def get_sales_orders_containing_product(self, product) -> List[dict]:
        values = {
            'product_id': product.id
        }

        cursor = self.get_cursor()
        cursor.execute("""SELECT DISTINCT sales_order_id
                            FROM sales_order_item
                            WHERE sales_order_item.product_id = %(product_id)s""", values)
        data = cursor.fetchall()
        cursor.close()
        if not data:
            return []
        return data
    
    def save_sales_order(self, sales_order) -> int:
        values = {
            'number': sales_order.number,
            'customer_name': sales_order.customer_name,
            'id': sales_order.id
        }

        cursor = self.get_cursor()
        if sales_order.id is None:
            cursor.execute("""INSERT INTO sales_order (number, customer_name)
                                VALUES(%(number)s, %(customer_name)s)""", values)
            sales_order_id = cursor.lastrowid
        else:
            cursor.execute("""UPDATE sales_order SET number = %(number)s, customer_name = %(customer_name)s
                                WHERE id = %(id)s""", values)
            sales_order_id = values["id"]
        cursor.execute("COMMIT;")
        cursor.close()
        return sales_order_id
    
    def delete_sales_order(self, sales_order) -> None:
        values = {
            'id': sales_order.id
        }
        
        # Iterate through all of the sales order items and delete them.
        for item in sales_order["sales_order_items"]:
            self.delete_sales_order_item(item)
        
        cursor = self.get_cursor()
        cursor.execute("DELETE FROM sales_order WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()
    
    # CutJobs methods
    def get_all_cut_jobs(self) -> List[dict]:
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM cut_job")
        cut_jobs = cursor.fetchall()
        cursor.close()
        if not cut_jobs:
            return []
        return cut_jobs

    def get_all_uncut_cut_jobs(self) -> List[dict]:
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM cut_job WHERE is_cut = 0")
        cut_jobs = cursor.fetchall()
        cursor.close()
        if not cut_jobs:
            return []
        return cut_jobs
    
    def get_all_open_cut_jobs(self) -> List[dict]:
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM cut_job WHERE is_ready_for_build = 0")
        cut_jobs = cursor.fetchall()
        cursor.close()
        if not cut_jobs:
            return []
        return cut_jobs

    def get_cut_jobs_by_product_number(self, product_number: str) -> List[dict]:
        cut_jobs = []
        data = self.get_product_by_number(product_number)
        if not data:
            return []
        for cut_job in self.get_all_cut_jobs():
            if cut_job["product_id"] != data["id"]:
                continue
            cut_jobs.append(cut_job)
        return cut_jobs
    
    def get_cut_jobs_by_so_item_id(self, so_item_id: int) -> List[dict]:
        values = {
            'so_item_id': so_item_id
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM cut_job WHERE related_sales_order_item_id = %(so_item_id)s", values)
        cut_jobs = cursor.fetchall()
        cursor.close()
        if not cut_jobs:
            return []
        return cut_jobs

    def get_cut_job_by_id(self, id: int) -> dict:
        values = {
            'id': id
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM cut_job WHERE id = %(id)s", values)
        cut_job = cursor.fetchone()
        cursor.close()
        if not cut_job:
            return None
        return cut_job
    
    def save_cut_job(self, cut_job) -> int:
        related_sales_order_item_id = None
        assigned_wire_cutter_id = None

        if cut_job.related_sales_order_item is not None:
            related_sales_order_item_id = cut_job.related_sales_order_item.id
        
        if cut_job.assigned_wire_cutter is not None:
            assigned_wire_cutter_id = cut_job.assigned_wire_cutter.id

        values = {
            'product_id': cut_job.product.id,
            'related_sales_order_item_id': related_sales_order_item_id,
            'assigned_wire_cutter_id': assigned_wire_cutter_id,
            'quantity_cut': cut_job.quantity_cut,
            'date_cut_start': cut_job.date_cut_start,
            'date_cut_end': cut_job.date_cut_end,
            'date_termination_start': cut_job.date_termination_start,
            'date_termination_end': cut_job.date_termination_end,
            'date_splice_start': cut_job.date_splice_start,
            'date_splice_end': cut_job.date_splice_end,
            'is_cut': cut_job.is_cut,
            'is_spliced': cut_job.is_spliced,
            'is_terminated': cut_job.is_terminated,
            'is_ready_for_build': cut_job.is_ready_for_build,
            'id': cut_job.id,
            'date_created': cut_job.date_created
        }

        cursor = self.get_cursor()
        if cut_job.id is None:
            cursor.execute("""INSERT INTO cut_job (product_id, related_sales_order_item_id, assigned_wire_cutter_id,
                                                    quantity_cut, date_cut_start, date_cut_end, date_termination_start, date_termination_end,
                                                    date_splice_start, date_splice_end, is_cut, is_spliced, is_terminated, is_ready_for_build, date_created)
                                VALUES(%(product_id)s, %(related_sales_order_item_id)s, %(assigned_wire_cutter_id)s,
                                %(quantity_cut)s, %(date_cut_start)s, %(date_cut_end)s, %(date_termination_start)s,
                                %(date_termination_end)s, %(date_splice_start)s, %(date_splice_end)s, %(is_cut)s,
                                %(is_spliced)s, %(is_terminated)s, %(is_ready_for_build)s, %(date_created)s)""", values)
            cut_job_id = cursor.lastrowid
        else:
            cursor.execute("""UPDATE cut_job SET product_id = %(product_id)s, related_sales_order_item_id = %(related_sales_order_item_id)s,
                                            assigned_wire_cutter_id = %(assigned_wire_cutter_id)s, quantity_cut = %(quantity_cut)s,
                                            date_cut_start = %(date_cut_start)s, date_cut_end = %(date_cut_end)s,
                                            date_termination_start = %(date_termination_start)s, date_termination_end = %(date_termination_end)s,
                                            date_splice_start = %(date_splice_start)s, date_splice_end = %(date_splice_end)s,
                                            is_cut = %(is_cut)s, is_spliced = %(is_spliced)s, is_terminated = %(is_terminated)s,
                                            is_ready_for_build = %(is_ready_for_build)s
                                            WHERE id = %(id)s""", values)
            cut_job_id = values["id"]
        cursor.execute("COMMIT;")
        cursor.close()
        return cut_job_id

    def delete_cut_job(self, cut_job: dict) -> None:
        values = {
            'id': cut_job["id"]
        }

        cursor = self.get_cursor()
        cursor.execute("DELETE FROM cut_job WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()

    # System Properties methods
    def get_all_system_properties(self) -> List[dict]:
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM system_properties")
        system_properties = cursor.fetchall()
        cursor.close()
        if not system_properties:
            return []
        return system_properties
    
    def get_system_property_by_name(self, name: str) -> dict:
        values = {
            'name': name
        }

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM system_properties WHERE name = %(name)s", values)
        system_property = cursor.fetchone()
        cursor.close()
        if not system_property:
            return None
        
        # Convert value from string to type stored in value_type column.
        if system_property["value_type"] == "int":
            system_property["value"] = int(system_property["value"])
        elif system_property["value_type"] == "float":
            system_property["value"] = float(system_property["value"])
        elif system_property["value_type"] == "bool":
            system_property["value"] = bool(int(system_property["value"]))
        elif system_property["value_type"] == "str":
            system_property["value"] = str(system_property["value"])
        elif system_property["value_type"] == "list":
            delimiter = self.get_system_property_by_name("list_to_string_delimiter")["value"]
            system_property["value"] = [item.strip() for item in system_property["value"].split(delimiter)]
        else:
            logger.warning(f"No type conversion for system property {system_property['name']} with value_type {system_property['value_type']}. Defaulting to str.")
        return system_property

    def save_system_property(self, system_property) -> int:
        value_type = type(system_property.value).__name__
        if isinstance(system_property.value, list):
            delimiter = self.get_system_property_by_name("list_to_string_delimiter")["value"]
            system_property.value = delimiter.join(system_property.value)

        values = {
            'name': system_property.name,
            'value': system_property.value,
            'date_last_modified': system_property.date_last_modified,
            'read_only': system_property.read_only,
            'visible': system_property.visible,
            'value_type': value_type,
            'id': system_property.id
        }

        cursor = self.get_cursor()
        if system_property.id is None:
            cursor.execute("""INSERT INTO system_properties (name, value, date_last_modified, read_only, visible, value_type)
                                VALUES(%(name)s, %(value)s,%(date_last_modified)s, %(read_only)s, %(visible)s, %(value_type)s)""", values)
            system_property_id = cursor.lastrowid
        else:
            cursor.execute("""UPDATE system_properties
                                SET name = %(name)s, value = %(value)s,
                                date_last_modified = %(date_last_modified)s,
                                read_only = %(read_only)s,
                                visible = %(visible)s,
                                value_type = %(value_type)s
                                WHERE id = %(id)s""", values)
            system_property_id = values["id"]
        cursor.execute("COMMIT;")
        cursor.close()
        return system_property_id

    def delete_system_property(self, system_property) -> None:
        values = {
            'id': system_property.id
        }

        cursor = self.get_cursor()
        cursor.execute("DELETE FROM system_properties WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()
    
    # Convenience methods
    def get_sales_order_table_data(self, search_data: dict) -> List[dict]:
        """Get table data for the sales order table."""
        cursor = self.get_cursor()
        

        if len(search_data) == 0:
            search_data = {
                'product_number': "%",
                'so_number': "%",
                'cut_in_full': 0,
            }

        if search_data['cut_in_full'] != '%':
            cursor.execute("""SELECT sales_order_item.id AS "Id",
                                DATE_FORMAT(sales_order_item.due_date, "%c-%e-%Y") AS "Due Date",
                                sales_order.customer_name AS "Customer Name",
                                sales_order.number AS "SO Number",
                                product.number AS "Product Number",
                                product.description AS "Description",
                                -- product.unit_price_dollars AS "Unit Price",
                                TRIM((sales_order_item.qty_to_fulfill - sales_order_item.qty_fulfilled - sales_order_item.qty_picked))+0 AS "Qty Left To Ship",
                                -- product.uom AS "UOM",
                                sales_order_item.line_number AS "Line Number",
                                product.kit_flag AS is_child_item,
                                sales_order_item.cut_in_full AS "Fully Cut",
                                parent_product.number AS "Parent Number",
                                parent_product.description AS "Parent Description"
                            FROM sales_order
                            JOIN sales_order_item ON sales_order_item.sales_order_id = sales_order.id
                            JOIN product ON sales_order_item.product_id = product.id
                            LEFT JOIN parent_to_child_product ON parent_to_child_product.child_product_id = product.id
                            LEFT JOIN product parent_product ON parent_to_child_product.parent_product_id = parent_product.id
                            WHERE sales_order_item.cut_in_full = 0
                            AND product.number LIKE%(product_number)s
                            AND sales_order.number LIKE%(so_number)s
                            ORDER BY product.number, sales_order_item.due_date""", search_data)
        else:
            cursor.execute("""SELECT sales_order_item.id AS "Id",
                                DATE_FORMAT(sales_order_item.due_date, "%c-%e-%Y") AS "Due Date",
                                sales_order.customer_name AS "Customer Name",
                                sales_order.number AS "SO Number",
                                product.number AS "Product Number",
                                product.description AS "Description",
                                -- product.unit_price_dollars AS "Unit Price",
                                TRIM((sales_order_item.qty_to_fulfill - sales_order_item.qty_fulfilled - sales_order_item.qty_picked))+0 AS "Qty Left To Ship",
                                -- product.uom AS "UOM",
                                sales_order_item.line_number AS "Line Number",
                                product.kit_flag AS is_child_item,
                                sales_order_item.cut_in_full AS "Fully Cut",
                                parent_product.number AS "Parent Number",
                                parent_product.description AS "Parent Description"
                            FROM sales_order
                            JOIN sales_order_item ON sales_order_item.sales_order_id = sales_order.id
                            JOIN product ON sales_order_item.product_id = product.id
                            LEFT JOIN parent_to_child_product ON parent_to_child_product.child_product_id = product.id
                            LEFT JOIN product parent_product ON parent_to_child_product.parent_product_id = parent_product.id
                            WHERE product.number LIKE%(product_number)s
                            AND sales_order.number LIKE%(so_number)s
                            ORDER BY product.number, sales_order_item.due_date""", search_data)

        sales_order_table_data = cursor.fetchall()
        cursor.close()
        return sales_order_table_data
    
    def get_exclude_product_numbers_from_import(self) -> List[str]:
        cursor = self.get_cursor()
        cursor.execute("SELECT number FROM exclude_product_number;")
        data = cursor.fetchall()
        cursor.close()
        return [row['number'] for row in data]
    
    def save_product_number_to_exclude(self, product_number: str) -> None:
        cursor = self.get_cursor()
        if product_number not in self.get_exclude_product_numbers_from_import():
            cursor.execute("INSERT INTO exclude_product_number (number) VALUES (%(product_number)s)", {'product_number': product_number})
            cursor.execute("COMMIT;")
        cursor.close()
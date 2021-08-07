import mysql.connector
# import datetime
# import decimal
# from mysql.connector import errorcode as mysql_errorcodes
# from mysql.connector import Error as mysql_error
from abc import ABC, abstractmethod
from typing import List
# from json import JSONEncoder


FISHBOWL_TO_CUT_LIST_DATABASE_MAPPING = {
    
}



# class DatabaseEncoder(JSONEncoder):
#         def default(self, obj):
#             if isinstance(obj, datetime.datetime):
#                 return obj.strftime("%Y-%m-%d %H:%M:%S")
#             elif isinstance(obj, decimal.Decimal):
#                 return float(obj)
#             else:
#                 return obj.__dict__


class Database(ABC):
    """Base class for Databases"""

    def __init__(self, connection_args: dict):
        """Initialize the Database"""

        self.connection = None
        self.connection_args = connection_args
    
    @abstractmethod
    def create(self):
        """Create the Database"""
        pass

    @abstractmethod
    def connect(self):
        """Connect to database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from database."""
        pass

    @abstractmethod
    def get_current_version(self):
        """Get the current version of the database."""
        pass


class CutListDatabase(Database):
    """Base class for CutList Databases"""

    # Product methods
    @abstractmethod
    def get_product_by_number(self, number: str) -> dict:
        """Get product by number. Returns None if not found."""
        pass

    @abstractmethod
    def get_all_products(self) -> List[dict]:
        """Get all products. Returns empty list if not found."""
        pass

    @abstractmethod
    def save_product(self, product: dict) -> int:
        """Save product to database. Returns id of saved product."""
        pass
    
    @abstractmethod
    def delete_product(self, product: dict) -> None:
        """Delete product from database."""
        pass
    
    # WireCutterOption methods
    @abstractmethod
    def get_wire_cutter_options_by_wire_cutter_name(self, wire_cutter_name: str) -> List[dict]:
        """Get wire cutter options by wire cutter name. Returns empty list if not found."""
        pass

    @abstractmethod
    def get_wire_cutter_option_by_name(self, option_name: str) -> dict:
        """Get wire cutter option by option name. Returns None if not found."""
        pass
    
    @abstractmethod
    def save_wire_cutter_option(self, wire_cutter_option: dict) -> int:
        """Save wire cutter option. Returns None if not found. Returns id of saved wire cutter option."""
        pass

    @abstractmethod
    def delete_wire_cutter_option(self, wire_cutter_option: dict) -> None:
        """Delete wire cutter option."""
        pass

    # WireCutter methods
    @abstractmethod
    def get_wire_cutter_by_name(self, name: str) -> dict:
        """Get wire cutter by name. Returns None if not found."""
        pass

    @abstractmethod
    def get_all_wire_cutters(self) -> List[dict]:
        """Get all wire cutters."""
        pass
    
    @abstractmethod
    def save_wire_cutter(self, wire_cutter: dict) -> int:
        """Save wire cutter. Returns id of saved wire cutter."""
        pass

    @abstractmethod
    def delete_wire_cutter(self, wire_cutter: dict) -> None:
        """Delete wire cutter."""
        pass

    # SalesOrder methods
    @abstractmethod
    def get_sales_order_by_number(self, number: str) -> dict:
        """Get sales order by number. Returns None if not found."""
        pass

    # @abstractmethod
    # def get_all_open_sales_orders(self) -> List[dict]:
    #     """Get all open sales orders. Returns empty list if not found."""
    #     pass

    @abstractmethod
    def get_all_sales_orders_by_customer_name(self, name: str) -> List[dict]:
        """Get all sales orders by customer name. Returns empty list if not found."""
        pass

    @abstractmethod
    def get_all_sales_orders(self) -> List[dict]:
        """Get all sales orders. Returns empty list if not found."""
        pass

    @abstractmethod
    def save_sales_order(self, sales_order: dict) -> int:
        """Save sales order. Returns id of saved sales order."""
        pass

    @abstractmethod
    def delete_sales_order(self, sales_order: dict) -> None:
        """Delete sales order."""
        pass

    # SalesOrderItem methods
    @abstractmethod
    def get_sales_order_items_by_sales_order_number(self, number: str) -> List[dict]:
        """Get all sales order items for sales order by number. Returns empty list if not found."""
        pass
    
    @abstractmethod
    def get_sales_order_items_by_sales_order_id(self, sales_order_id: int) -> List[dict]:
        """Get all sales order items for sales order by number. Returns empty list if not found."""
        pass

    @abstractmethod
    def get_sales_order_item_by_id(self, sales_order_id: int) -> List[dict]:
        """Gets a sales order item by sales order id. Returns empty list if not found."""
        pass

    @abstractmethod
    def save_sales_order_item(self, sales_order_item: dict) -> int:
        """Save sales order item. Returns id of saved sales order item."""
        pass

    @abstractmethod
    def delete_sales_order_item(self, sales_order_item: dict) -> None:
        """Delete sales order item."""
        pass

    # CutJobs methods
    @abstractmethod
    def get_all_cut_jobs(self) -> List[dict]:
        """Get all cut jobs. Returns empty list if not found."""
        pass

    @abstractmethod
    def get_all_open_cut_jobs(self) -> List[dict]:
        """Get all open cut jobs. Returns empty list if not found."""
        pass

    @abstractmethod
    def get_cut_job_by_product_number(self, product_number: str) -> dict:
        """Get cut job by product number. Returns None if not found."""
        pass

    @abstractmethod
    def get_cut_job_by_id(self, id: int) -> dict:
        """Get cut job by id. Returns None if not found."""
        pass
    
    @abstractmethod
    def save_cut_job(self, cut_job: dict) -> int:
        """Save cut job. Returns id of saved cut job."""
        pass

    @abstractmethod
    def delete_cut_job(self, cut_job: dict) -> None:
        """Delete cut job."""
        pass


class MySQLDatabaseConnection(CutListDatabase):
    """MySQL Database Connection"""

    def connect(self):
        self.connection = mysql.connector.connect(**self.connection_args)

    def __get_cursor(self, buffered=None, raw=None, prepared=None, cursor_class=None, dictionary=True, named_tuple=None):
        """Get a cursor to the database. Defaults to a dictionary cursor."""
        if not self.connection:
            self.connect()

        return self.connection.cursor(buffered, raw, prepared, cursor_class, dictionary, named_tuple)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_current_version(self) -> dict:
        cursor = self.__get_cursor()
        cursor.execute("SELECT * FROM database_version ORDER BY id DESC LIMIT 1")
        return cursor.fetchone()
    
    def get_product_by_number(self, number: str) -> dict:
        cursor = self.__get_cursor()
        values = {
            'number': number
        }

        cursor.execute("SELECT * FROM product WHERE number = %(number)s", values)
        product = cursor.fetchone()
        cursor.close()
        if not product:
            return None
        return product
    
    def get_all_products(self) -> List[dict]:
        cursor = self.__get_cursor()
        cursor.execute("SELECT * FROM product")
        products = cursor.fetchall()
        cursor.close()
        if not products:
            return []
        return products
    
    def save_product(self, product: dict) -> int:
        values = {
            'number': product['number'],
            'description': product['description'],
            'uom': product['uom'],
            'unit_price_dollars': product['unit_price_dollars'],
            'kit_flag': product['kit_flag'],
            'parent_kit_product_number': product['parent_kit_product_number'],
            'id': product['id']
        }

        cursor = self.__get_cursor()

        if product["id"] is None:
            cursor.execute("""INSERT INTO product (number, description, uom, unit_price_dollars, kit_flag, parent_kit_product_number)
                                VALUES(%(number)s, %(description)s, %(uom)s, %(unit_price_dollars)s, %(kit_flag)s, %(parent_kit_product_number)s)""", values)
            product_id = cursor.lastrowid
        else:
            cursor.execute("""UPDATE product SET number = %(number)s, description = %(description)s, uom = %(uom)s,
                                unit_price_dollars = %(unit_price_dollars)s, kit_flag = %(kit_flag)s, parent_kit_product_number = %(parent_kit_product_number)s
                                WHERE id = %(id)s""", values)
            product_id = values["id"]
        cursor.execute("COMMIT;")
        cursor.close()
        return product_id
    
    def delete_product(self, product: dict) -> None:
        values = {
            'id': product["id"]
        }

        cursor = self.__get_cursor()
        cursor.execute("DELETE FROM product WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()
    
    # WireCutterOptions methods
    def get_wire_cutter_option_by_id(self, wire_cutter_option_id: int) -> dict:
        values = {
            'id': wire_cutter_option_id
        }

        cursor = self.__get_cursor()
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

        cursor = self.__get_cursor()
        cursor.execute("SELECT * FROM wire_cutter_option WHERE name = %(name)s", values)
        wire_cutter_option = cursor.fetchone()
        cursor.close()
        if not wire_cutter_option:
            return None
        return wire_cutter_option
    
    def get_wire_cutter_options_by_wire_cutter_name(self, wire_cutter_name: str) -> List[dict]:
        values = {
            'wire_cutter_name': wire_cutter_name
        }

        cursor = self.__get_cursor()
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
    
    def save_wire_cutter_option(self, wire_cutter_option: dict) -> int:
        values = {
            'name': wire_cutter_option['name'],
            'description': wire_cutter_option['description'],
            'id': wire_cutter_option['id']
        }

        cursor = self.__get_cursor()
        if wire_cutter_option["id"] is None:
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
    
    def delete_wire_cutter_option(self, wire_cutter_option: dict) -> None:
        values = {
            'id': wire_cutter_option["id"]
        }

        cursor = self.__get_cursor()
        cursor.execute("DELETE FROM wire_cutter_option WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()

    # WireCutter methods
    def get_wire_cutter_by_name(self, wire_cutter_name: str) -> dict:
        values = {
            'wire_cutter_name': wire_cutter_name
        }

        cursor = self.__get_cursor()
        cursor.execute("SELECT * FROM wire_cutter WHERE name = %(name)s", values)
        wire_cutter = cursor.fetchone()
        cursor.close()
        if not wire_cutter:
            return None
        return wire_cutter

    def get_all_wire_cutters(self) -> List[dict]:
        cursor = self.__get_cursor()
        cursor.execute("SELECT * FROM wire_cutter")
        wire_cutters = cursor.fetchall()
        cursor.close()
        if not wire_cutters:
            return []
        return wire_cutters

    def save_wire_cutter(self, wire_cutter: dict) -> int:
        values = {
            'name': wire_cutter['name'],
            'max_wire_gauge_awg': wire_cutter['max_wire_gauge_awg'],
            'processing_speed_feet_per_minute': wire_cutter['processing_speed_feet_per_minute'],
            'details': wire_cutter['details'],
            'id': wire_cutter['id']
        }
        cursor = self.__get_cursor()

        # Save the wire_cutter
        if wire_cutter["id"] is None:
            cursor.execute("""INSERT INTO wire_cutter (name, max_wire_gauge_awg, processing_speed_feet_per_minute, details)
                                VALUES(%(name)s, %(max_wire_gauge_awg)s, %(processing_speed_feet_per_minute)s, %(details)s)""", values)
            wire_cutter_id = cursor.lastrowid
        else:
            cursor.execute("""UPDATE wire_cutter SET name = %(name)s, max_wire_gauge_awg = %(max_wire_gauge_awg)s, processing_speed_feet_per_minute = %(processing_speed_feet_per_minute)s, details = %(details)s
                                WHERE id = %(id)s""", values)
            wire_cutter_id = values["id"]
        
        # Save the wire_cutter_to_wire_cutter_option relationship
        for wire_cutter_option in wire_cutter["wire_cutter_options"]:
            values = {
                'wire_cutter_id': wire_cutter_id,
                'wire_cutter_option_id': wire_cutter_option["id"]
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
    
    def delete_wire_cutter(self, wire_cutter: dict) -> None:
        values = {
            'id': wire_cutter["id"]
        }

        cursor = self.__get_cursor()
        cursor.execute("DELETE FROM wire_cutter WHERE id = %(id)s", values)

        # Delete the wire_cutter_to_wire_cutter_option relationship
        cursor.execute("""
            DELETE FROM wire_cutter_to_wire_cutter_option
            WHERE wire_cutter_id = %(id)s""", values)
        cursor.execute("COMMIT;")
        cursor.close()
    
    # Sales Order Item methods
    def get_sales_order_items_by_sales_order_id(self, sales_order_id: int) -> List[dict]:
        values = {
            'sales_order_id': sales_order_id
        }

        cursor = self.__get_cursor()
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

        cursor = self.__get_cursor()
        cursor.execute("SELECT * FROM sales_order_item WHERE id = %(id)s", values)
        sales_order_item = cursor.fetchone()
        cursor.close()
        if not sales_order_item:
            return None
        return sales_order_item
    
    def get_sales_order_items_by_sales_order_number(self, number: str) -> List[dict]:
        values = {
            'number': number
        }

        cursor = self.__get_cursor()
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
    
    def save_sales_order_item(self, sales_order_item: dict) -> int:
        values = {
            'sales_order_id': sales_order_item['sales_order_id'],
            'due_date': sales_order_item['due_date'],
            'name': sales_order_item['name'],
            'product_id': sales_order_item['product']['id'],
            'quantity_requseted': sales_order_item['quantity_requseted'],
            'line_number': sales_order_item['line_number'],
            'id': sales_order_item['id']
        }

        cursor = self.__get_cursor()
        if sales_order_item["id"] is None:
            cursor.execute("""INSERT INTO sales_order_item (sales_order_id, name, due_date, product_id, quantity_requseted, line_number)
                                VALUES(%(sales_order_id)s, %(name)s, %(due_date)s, %(product_id)s, %(quantity_requseted)s, %(line_number)s)""", values)
            sales_order_item_id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE sales_order_item
                SET sales_order_id = %(sales_order_id)s,
                name = %(name)s,
                due_date = %(due_date)s,
                product_id = %(product_id)s,
                quantity_requseted = %(quantity_requseted)s,
                line_number = %(line_number)s
                WHERE id = %(id)s""", values)
            sales_order_item_id = values["id"]
        cursor.execute("COMMIT;")
        cursor.close()
        return sales_order_item_id
        
    def delete_sales_order_item(self, sales_order_item: dict) -> None:
        values = {
            'id': sales_order_item["id"]
        }

        cursor = self.__get_cursor()
        cursor.execute("DELETE FROM sales_order_item WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()
    
    # Sales Order methods
    def get_sales_order_by_number(self, number: str) -> dict:
        values = {
            'number': number
        }

        cursor = self.__get_cursor()
        cursor.execute("SELECT * FROM sales_order WHERE number = %(number)s", values)
        sales_order = cursor.fetchone()
        cursor.close()
        if not sales_order:
            return None
        return sales_order

    def get_all_sales_orders(self) -> List[dict]:
        cursor = self.__get_cursor()
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
    
    def save_sales_order(self, sales_order: dict) -> int:
        values = {
            'number': sales_order['number'],
            'customer_name': sales_order['customer_name'],
            'details': sales_order['details'],
            'id': sales_order['id']
        }

        cursor = self.__get_cursor()
        if sales_order["id"] is None:
            cursor.execute("""INSERT INTO sales_order (number, customer_name, details)
                                VALUES(%(number)s, %(customer_name)s, %(details)s)""", values)
            sales_order_id = cursor.lastrowid
        else:
            cursor.execute("""UPDATE sales_order SET number = %(number)s, customer_name = %(customer_name)s details = %(details)s
                                WHERE id = %(id)s""", values)
            sales_order_id = values["id"]
        cursor.execute("COMMIT;")
        cursor.close()
        return sales_order_id
    
    def delete_sales_order(self, sales_order: dict) -> None:
        values = {
            'id': sales_order["id"]
        }
        
        # Iterate through all of the sales order items and delete them.
        for item in sales_order["sales_order_items"]:
            self.delete_sales_order_item(item)
    
    # CutJobs methods
    def get_all_cut_jobs(self) -> List[dict]:
        pass

    def get_all_open_cut_jobs(self) -> List[dict]:
        pass

    def get_cut_job_by_product_number(self, product_number: str) -> dict:
        pass

    def get_cut_job_by_id(self, id: int) -> dict:
        pass
    
    def save_cut_job(self, cut_job: dict) -> int:
        pass

    def delete_cut_job(self, cut_job: dict) -> None:
        values = {
            'id': cut_job["id"]
        }

        cursor = self.__get_cursor()
        cursor.execute("DELETE FROM cut_job WHERE id = %(id)s", values)
        cursor.execute("COMMIT;")
        cursor.close()


class FishbowlDatabase(Database):
    """MySQL database connection to a Fishbowl database."""
    
    def connect(self):
        self.connection = mysql.connector.connect(**self.connection_args)
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create(self):
        raise NotImplementedError("This method is not implemented. A Fishbowl database must be created when installing Fishbowl.")
    
    def get_current_version(self) -> dict:
        cursor = self.__get_cursor()
        cursor.execute("SELECT * FROM databaseversion ORDER BY id DESC LIMIT 1")
        return cursor.fetchone()

    def __get_cursor(self, buffered=None, raw=None, prepared=None, cursor_class=None, dictionary=True, named_tuple=None):
        """Get a cursor to the database. Defaults to a dictionary cursor."""
        if not self.connection:
            self.connect()

        return self.connection.cursor(buffered, raw, prepared, cursor_class, dictionary, named_tuple)

    def get_all_open_sales_order_items(self) -> List[dict]:
        cursor = self.__get_cursor()
        cursor.execute("""
                SELECT so.num AS soNum,
                    CASE 
                        WHEN customer.name = "Brunswick Boat Group, Fort Wayne Operatio" THEN "Brunswick"
                        WHEN customer.name = "GODFREY MARINE-HURRICANE" THEN "Godfrey"
                        WHEN customer.name = "MARINE MOORING, INC." THEN "Marine Mooring"
                        WHEN customer.name = "Bennington Pontoon Boats" THEN "Bennington"
                        ELSE customer.name
                    END AS customer_name,
                    DATE(so.dateFirstShip) AS due_date,
                    -- DATE_SUB(so.dateFirstShip, INTERVAL 14 DAY) AS cutDate,
                    soitem.soLineItem AS line_number,
                    product.num AS product_number,
                    product.description,
                    soitem.qtyToFulfill AS qty_to_fulfill,
                    soitem.qtyPicked AS qty_picked,
                    soitem.qtyFulfilled AS qty_fulfilled,
                    productuom.code AS uom
                FROM so
                JOIN soitem ON soitem.soId = so.id
                JOIN customer ON so.customerId = customer.id
                JOIN product ON soitem.productId = product.id
                JOIN uom productuom ON product.uomId = productuom.id
                WHERE soitem.statusId < 50 -- 50 = Finished
                AND (soitem.qtyToFulfill - qtyPicked - qtyFulfilled) > 0
                -- AND DATE_SUB(so.dateFirstShip, INTERVAL 14 DAY) < NOW()
                AND product.num LIKE "50%"
                AND productuom.code = "ea";
        """)
        data = cursor.fetchall()
        cursor.close()
        if not data:
            return []
        return data
    
    def get_kit_items_for_product_number(self, product_number: str) -> List[dict]:
        """Finds all the kit items for a product number. Returns a list of dictionaries
            with the product number, kit_part_number, and kit_part_qty as keys."""

        kit_items = []

        cursor = self.__get_cursor()
        values = {
            'product_number': product_number
        }

        cursor.execute("""
            SELECT 
                -- finishedpart.num AS product_number,
                rawpart.num AS kit_part_number,
                bomitem.quantity AS kit_part_quantity
            FROM product
            JOIN part finishedpart ON product.partId = finishedpart.id
            JOIN bomitem ON finishedpart.defaultBomId = bomitem.bomId
            JOIN part rawpart ON bomitem.partId = rawpart.id
            WHERE product.num = %(product_number)s
            AND bomitem.typeId = (
                                SELECT id
                                FROM bomitemtype
                                WHERE name = "Raw Good"
                                )
            AND ((rawpart.num LIKE "BC-10%" AND rawpart.uomId = (SELECT id FROM uom WHERE name = "Each")) OR rawpart.num LIKE "50%")
            AND rawpart.typeId = (SELECT id FROM parttype WHERE name = "Inventory");
        """, values)
        kit_items = cursor.fetchall()
        cursor.close()
        if not kit_items:
            return []
        return kit_items

    def get_kit_items_for_product_number_recursively(self, product_number: str) -> List[dict]:
        """Finds all kit items for a product number recursively(i.e. for all kit parts). Retruns
            a dictionary list for all items. Each dictionary contains the kit_part_number and kit_part_quantity."""

        kit_items = self.get_kit_items_for_product_number(product_number)

        # TODO: Change this to multiply the quantity of the kit part by the quantity of the next kit part.
        # TODO: Check if this works as expected.

        kit_item_list = []
        for kit_item in kit_items:
            # kit_item_list.append(kit_item)
            kit_part_number = kit_item['kit_part_number']
            # kit_part_quantity = kit_item['kit_part_quantity']
            kit_data = self.get_kit_items_for_product_number_recursively(kit_part_number)

            if not kit_data:
                kit_item_list.append(kit_item)
                continue

            kit_item_list.extend(kit_data)
        
        return kit_item_list
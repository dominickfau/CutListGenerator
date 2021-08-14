from . import *

from cutlistgenerator.logging import FileLogger

logger = FileLogger(__name__)


class FishbowlDatabaseConnection(Database):
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
        """Returns a list of dictionaries containing the sales order number, product number,
        and product name for all open sales order items."""

        logger.info("[FISHBOWL] Searching for open sales orders.")

        cursor = self.__get_cursor()
        cursor.execute("""
                SELECT so.num AS so_number,
                    CASE 
                        WHEN customer.name = "Brunswick Boat Group, Fort Wayne Operatio" THEN "Brunswick"
                        WHEN customer.name = "GODFREY MARINE-HURRICANE" THEN "Godfrey"
                        WHEN customer.name = "MARINE MOORING, INC." THEN "Marine Mooring"
                        WHEN customer.name = "Bennington Pontoon Boats" THEN "Bennington"
                        ELSE customer.name
                    END AS customer_name,
                    CASE
                        WHEN customerparts.lastPrice THEN customerparts.lastPrice
                        ELSE product.price
                    END AS unit_price_dollars,
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
                LEFT JOIN customerparts ON product.id = customerparts.productId AND customer.id = customerparts.customerId
                JOIN uom productuom ON product.uomId = productuom.id
                WHERE soitem.statusId < 50 -- 50 = Finished
                AND (soitem.qtyToFulfill - qtyPicked - qtyFulfilled) > 0
                -- AND DATE_SUB(so.dateFirstShip, INTERVAL 14 DAY) < NOW()
                AND productuom.code = "ea";
        """)
        data = cursor.fetchall()
        cursor.close()
        if not data:
            logger.info("[FISHBOWL] No open sales order items found.")
            return []
        logger.info(f"[FISHBOWL] Found {len(data)} open sales order items.")
        return data
    
    def get_kit_items_for_product_number(self, product_number: str) -> List[dict]:
        """Finds all the kit items for a product number. Returns a list of dictionaries
            with the child_part_number, and child_part_qty as keys."""

        logger.debug(f"[FISHBOWL] Searching for child kit items for product number {product_number}.")
        kit_items = []

        cursor = self.__get_cursor()
        values = {
            'product_number': product_number
        }

        cursor.execute("""
            SELECT 
                -- finishedpart.num AS product_number,
                rawpart.num AS child_part_number,
                bomitem.quantity AS child_part_quantity
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
            AND ((CHAR_LENGTH(rawpart.num) >= 11 AND rawpart.uomId = (SELECT id FROM uom WHERE name = "Each")) OR rawpart.num LIKE "50%")
            AND rawpart.typeId = (SELECT id FROM parttype WHERE name = "Inventory");
        """, values)
        kit_items = cursor.fetchall()
        cursor.close()
        if not kit_items:
            logger.debug(f"[FISHBOWL] No child kit items found for product number {product_number}.")
            return []
        logger.debug(f"[FISHBOWL] Found {len(kit_items)} child kit items for product number {product_number}.")
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
    
    def get_product_data_from_number(self, product_number: str) -> dict:
        """Gets product data for a product number. Returns a dictionary with the product number, description, and unit price. Returns None if no product is found."""
        
        logger.debug(f"[FISHBOWL] Searching for product data for product number {product_number}.")
        values = {
            'product_number': product_number
        }

        cursor = self.__get_cursor()
        cursor.execute("""
            SELECT product.num AS product_number,
                product.description AS description,
                product.price AS unit_price_dollars,
                uom.code AS uom
            FROM product
            JOIN uom ON product.uomId = uom.id
            WHERE product.num = %(product_number)s;
            """, values)
        product_data = cursor.fetchone()
        cursor.close()
        if not product_data:
            logger.debug(f"[FISHBOWL] No product data found for product number {product_number}.")
            return None
        logger.debug(f"[FISHBOWL] Found product data for product number {product_number}.")
        return product_data
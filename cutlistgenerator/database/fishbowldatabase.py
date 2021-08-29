from . import *


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
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM databaseversion ORDER BY id DESC LIMIT 1")
        return cursor.fetchone()

    def get_cursor(self, buffered=None, raw=None, prepared=None, cursor_class=None, dictionary=True, named_tuple=None):
        """Get a cursor to the database. Defaults to a dictionary cursor."""
        if not self.connection:
            self.connect()

        return self.connection.cursor(buffered, raw, prepared, cursor_class, dictionary, named_tuple)

    def get_all_open_sales_order_items(self) -> List[dict]:
        """Returns a list of dictionaries containing the sales order number, product number,
        and product name for all open sales order items."""

        cursor = self.get_cursor()
        # CASE 
        #     WHEN customer.name = "Brunswick Boat Group, Fort Wayne Operatio" THEN "Brunswick"
        #     WHEN customer.name = "GODFREY MARINE-HURRICANE" THEN "Godfrey"
        #     WHEN customer.name = "MARINE MOORING, INC." THEN "Marine Mooring"
        #     WHEN customer.name = "Bennington Pontoon Boats" THEN "Bennington"
        #     ELSE customer.name
        # END AS customer_name,

        cursor.execute("""
                SELECT so.id AS so_id,
                    so.num AS so_number,
                    customer.name AS customer_name,
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
                AND productuom.code = "ea"
                ORDER BY so.num, product.num;
        """)
        data = cursor.fetchall()
        cursor.close()
        if not data:
            return []
        return data
    
    def get_child_products_for_product_number(self, product_number: str) -> List[dict]:
        """Returns a dictionary list of all child items for a product number. Returns an empty list if no child items are found."""
        values = {
            'product_number': product_number
        }

        cursor = self.get_cursor()
        cursor.execute("""SELECT DISTINCT
                            rawpart.num AS kit_part_number,
                            rawpart.description AS kit_part_description
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
                        AND (rawpart.num LIKE "500%" OR (replace(UPPER(rawpart.num), "BC-", "") >= 10000000 AND rawpart.num LIKE "BC-%"))
                        AND rawpart.typeId = (SELECT id FROM parttype WHERE name = "Inventory");
                        """, values)
        data = cursor.fetchall()
        cursor.close()
        if not data:
            return []
        return data
    
    def get_product_data_from_number(self, product_number: str) -> dict:
        """Gets product data for a product number. Returns a dictionary with the product number, description, and unit price. Returns None if no product is found."""
        
        values = {
            'product_number': product_number
        }

        cursor = self.get_cursor()
        cursor.execute("""
            SELECT product.num AS number,
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
            return None
        return product_data
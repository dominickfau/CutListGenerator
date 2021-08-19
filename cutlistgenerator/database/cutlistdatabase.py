from . import abstractmethod, List
from . import Database


class CutListDatabase(Database):
    """Base class for CutList Databases"""

    @abstractmethod
    def create(self):
        """Create the database"""
        pass

    # Product methods
    @abstractmethod
    def get_product_by_number(self, number: str) -> dict:
        """Get product by number. Returns None if not found."""
        pass

    @abstractmethod
    def get_product_by_id(self, id: int) -> dict:
        """Get product by ID. Returns None if not found."""
        pass

    @abstractmethod
    def get_all_products(self) -> List[dict]:
        """Get all products. Returns empty list if not found."""
        pass

    @abstractmethod
    def save_product(self, product) -> int:
        """Save product to database. Returns id of saved product."""
        pass
    
    @abstractmethod
    def delete_product(self, product) -> None:
        """Delete product from database."""
        pass
    
    @abstractmethod
    def get_parent_product_from_child_product_id(self, child_product_id) -> dict:
        """Gets the parent product from a child product ID. Returns None if not found."""
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
    def save_wire_cutter_option(self, wire_cutter_option) -> int:
        """Save wire cutter option. Returns None if not found. Returns id of saved wire cutter option."""
        pass

    @abstractmethod
    def delete_wire_cutter_option(self, wire_cutter_option) -> None:
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
    def save_wire_cutter(self, wire_cutter) -> int:
        """Save wire cutter. Returns id of saved wire cutter."""
        pass

    @abstractmethod
    def delete_wire_cutter(self, wire_cutter) -> None:
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
    def save_sales_order(self, sales_order) -> int:
        """Save sales order. Returns id of saved sales order."""
        pass

    @abstractmethod
    def delete_sales_order(self, sales_order) -> None:
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
    def save_sales_order_item(self, sales_order_item) -> int:
        """Save sales order item. Returns id of saved sales order item."""
        pass

    @abstractmethod
    def delete_sales_order_item(self, sales_order_item) -> None:
        """Delete sales order item."""
        pass

    # CutJobs methods
    @abstractmethod
    def get_all_cut_jobs(self) -> List[dict]:
        """Get all cut jobs. Returns empty list if not found."""
        pass

    @abstractmethod
    def get_all_uncut_cut_jobs(self) -> List[dict]:
        """Get all cut jobs that have not been cut. Returns empty list if not found."""
        pass

    @abstractmethod
    def get_cut_jobs_by_product_number(self, product_number: str) -> List[dict]:
        """Get cut jobs by product number. Returns empty list if not found."""
        pass

    @abstractmethod
    def get_cut_job_by_id(self, id: int) -> dict:
        """Get cut job by id. Returns None if not found."""
        pass
    
    @abstractmethod
    def save_cut_job(self, cut_job) -> int:
        """Save cut job. Returns id of saved cut job."""
        pass

    @abstractmethod
    def delete_cut_job(self, cut_job) -> None:
        """Delete cut job."""
        pass

    # System Properties methods
    @abstractmethod
    def get_all_system_properties(self) -> List[dict]:
        """Get all system properties. Returns empty list if not found."""
        pass
    
    @abstractmethod
    def get_system_property_by_name(self, name: str) -> dict:
        """Get system property by name. Returns None if not found."""
        pass

    @abstractmethod
    def save_system_property(self, system_property) -> int:
        """Save system property. Returns id of saved system property."""
        pass

    @abstractmethod
    def delete_system_property(self, system_property) -> None:
        """Delete system property."""
        pass
    
    # Convenience methods
    @abstractmethod
    def get_sales_order_table_data(self, search_data: dict) -> List[dict]:
        """Get table data for the sales order table."""
        pass
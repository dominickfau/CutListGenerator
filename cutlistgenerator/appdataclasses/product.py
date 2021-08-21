from . import dataclass, List
from . import CutListDatabase
from cutlistgenerator.error import ProductNotInKitError


@dataclass
class Product:
    """Represents a product."""

    database_connection: CutListDatabase
    number: str
    description: str
    uom: str
    unit_price_dollars: float = None
    kit_flag: bool = False
    parent_kit_product: 'Product' = None
    id: int = None

    def __post_init__(self):
        """Initialize the product after it's been created."""
        
        if self.kit_flag and self.parent_kit_product is None:
            raise ProductNotInKitError("Product is marked as a kit but does not have a parent kit product.")

        if self.unit_price_dollars is None:
            self.unit_price_dollars = 0.0

    @staticmethod
    def find_parent_kit_product_from_child_product_data(database_connection, product_data: dict) -> dict:
        """Finds the parent kit product from the child product data. Returns product data with 'parent_kit_product' key populated."""

        parent_kit_product = None
        parent_kit_product_data = database_connection.get_parent_product_from_child_product_id(product_data['id'])
        if parent_kit_product_data:
            parent_kit_product = Product.from_number(database_connection, parent_kit_product_data['number'])
        
        product_data['parent_kit_product'] = parent_kit_product
        return product_data

    @classmethod
    def from_number(cls, database_connection: CutListDatabase, number: str) -> 'Product':
        """Returns a product from the database by its number. Returns None if not found."""

        data = database_connection.get_product_by_number(number)
        if not data:
            return None
        
        data = cls.find_parent_kit_product_from_child_product_data(database_connection, data)

        return cls(database_connection, **data)
    
    @classmethod
    def get_all(cls, database_connection: CutListDatabase) -> List['Product']:
        """Returns all products."""

        return [cls.from_number(database_connection, product_data['number']) for product_data in database_connection.get_all_products()]
    
    @classmethod
    def from_id(cls, database_connection: CutListDatabase, id: int) -> 'Product':
        """Returns a product from the database by its ID. Returns None if not found."""

        data = database_connection.get_product_by_id(id)
        if not data:
            return None
        
        data = cls.find_parent_kit_product_from_child_product_data(database_connection, data)

        return cls(database_connection, **data)
    
    def set_parent_kit_product(self, parent_kit_product: 'Product'):
        """Sets the parent kit product number for this product."""

        self.parent_kit_product = parent_kit_product
        self.kit_flag = True
    
    def save(self):
        """Saves the product to the database."""

        self.id = self.database_connection.save_product(self)
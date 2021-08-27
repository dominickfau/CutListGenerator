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
    child_products: List['Product'] = None
    id: int = None

    def __post_init__(self):
        """Initialize the product after it's been created."""
        
        if self.kit_flag and self.child_products is None:
            raise ProductNotInKitError("Product is marked as a kit but does not have child products.")
        
        if self.child_products is None:
            self.child_products = []

        if self.unit_price_dollars is None:
            self.unit_price_dollars = 0.0
    
    @property
    def kit_flag_as_string(self) -> str:
        """Returns the kit flag as a string."""
        if self.kit_flag:
            return "Yes"
        return "No"

    @staticmethod
    def find_child_products_from_parent_product_data(database_connection: CutListDatabase, product_data: dict) -> dict:
        """Finds the child products from the parent product data. Returns product data with 'child_products' key populated."""

        child_products = []
        child_products_data = database_connection.get_child_products_from_parent_product_id(product_data['id'])
        for child_product_data in child_products_data:
            child_product = Product.from_number(database_connection, child_product_data['number'])
            child_products.append(child_product)
            
        product_data['child_products'] = child_products
        return product_data

    @classmethod
    def from_number(cls, database_connection: CutListDatabase, number: str) -> 'Product':
        """Returns a product from the database by its number. Returns None if not found."""

        data = database_connection.get_product_by_number(number)
        if not data:
            return None
        
        data = cls.find_child_products_from_parent_product_data(database_connection, data)

        return cls(database_connection, **data)
    
    @classmethod
    def get_all(cls, database_connection: CutListDatabase) -> List['Product']:
        """Returns all products."""

        return [cls.from_number(database_connection, product_data['number']) for product_data in database_connection.get_all_products()]
    
    @classmethod
    def from_id(cls, database_connection: CutListDatabase, id: int) -> 'Product':
        """Returns a product from the database by its ID. Returns None if not found."""
        if not id:
            return None
        data = database_connection.get_product_by_id(id)
        if not data:
            return None
        
        data = cls.find_child_products_from_parent_product_data(database_connection, data)

        return cls(database_connection, **data)
    
    def add_child_product(self, child_product: 'Product'):
        """Adds a child product."""
        if not child_product:
            return
        self.kit_flag = True
        if child_product not in self.child_products:
            self.child_products.append(child_product)
    
    def save(self):
        """Saves the product to the database."""

        self.id = self.database_connection.save_product(self)

        for child_product in self.child_products:
            child_product.save()
            self.database_connection.save_product_relationship(self.id, child_product.id)
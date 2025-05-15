"""
Product classes and exceptions for the Inventory Management System.
This file defines the product types (Physical, Digital, Service) and their behavior.
"""

# Step 1: Import necessary libraries
# - abc: For creating abstract base classes
# - datetime: For tracking creation and update times
# - typing: For type hints
# - uuid: For generating unique IDs
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List
import uuid


# Step 2: Define the abstract Product class
class Product(ABC):
    """Abstract base class for all products in the inventory system.
    This defines common attributes and methods for all product types.
    """
    
    # Step 2.1: Class variable for ID generation (not used since we switched to UUID)
    _id_counter = 1  # Class variable for generating unique IDs
    
    # Step 2.2: Initialize a product
    def __init__(self, name: str, price: float, quantity: int, category: str):
        """Initialize a product with basic attributes.
        Args:
            name: Product name
            price: Product price
            quantity: Number of items in stock
            category: Product category
        """
        # Generate a unique ID using the first 8 characters of a UUID
        self._id = str(uuid.uuid4())[:8]
        # Store the name, price, quantity, and category
        self._name = name
        self._price = float(price)
        self._quantity = int(quantity)
        self._category = category
        # Record the creation and update times
        self._created_at = datetime.now()
        self._updated_at = self._created_at
    
    # Step 2.3: Properties to get attributes (read-only)
    @property
    def id(self) -> str:
        """Get the product ID.
        Returns:
            The unique ID of the product
        """
        return self._id
    
    @property
    def name(self) -> str:
        """Get the product name.
        Returns:
            The name of the product
        """
        return self._name
    
    # Step 2.4: Setter for name with validation
    @name.setter
    def name(self, value: str) -> None:
        """Set the product name.
        Args:
            value: The new name
        """
        # Ensure the name is not empty
        if not value.strip():
            raise ValueError("Product name cannot be empty")
        self._name = value
        # Update the timestamp
        self._updated_at = datetime.now()
    
    @property
    def price(self) -> float:
        """Get the product price.
        Returns:
            The price of the product
        """
        return self._price
    
    @price.setter
    def price(self, value: float) -> None:
        """Set the product price.
        Args:
            value: The new price
        """
        # Ensure the price is not negative
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = float(value)
        self._updated_at = datetime.now()
    
    @property
    def quantity(self) -> int:
        """Get the product quantity.
        Returns:
            The number of items in stock
        """
        return self._quantity
    
    @quantity.setter
    def quantity(self, value: int) -> None:
        """Set the product quantity.
        Args:
            value: The new quantity
        """
        # Ensure the quantity is not negative
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        self._quantity = int(value)
        self._updated_at = datetime.now()
    
    @property
    def category(self) -> str:
        """Get the product category.
        Returns:
            The category of the product
        """
        return self._category
    
    @category.setter
    def category(self, value: str) -> None:
        """Set the product category.
        Args:
            value: The new category
        """
        # Ensure the category is not empty
        if not value.strip():
            raise ValueError("Category cannot be empty")
        self._category = value
        self._updated_at = datetime.now()
    
    @property
    def created_at(self) -> datetime:
        """Get the creation date and time.
        Returns:
            When the product was created
        """
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """Get the last update date and time.
        Returns:
            When the product was last updated
        """
        return self._updated_at
    
    @property
    def value(self) -> float:
        """Calculate the total value of this product (price * quantity).
        Returns:
            The total value of all items in stock
        """
        return self._price * self._quantity
    
    # Step 2.5: Add stock to the product
    def add_stock(self, amount: int) -> None:
        """Add stock to the product.
        Args:
            amount: The number of items to add
        """
        # Ensure the amount is not negative
        if amount < 0:
            raise ValueError("Amount to add cannot be negative")
        self._quantity += amount
        self._updated_at = datetime.now()
    
    # Step 2.6: Remove stock from the product
    def remove_stock(self, amount: int) -> None:
        """Remove stock from the product.
        Args:
            amount: The number of items to remove
        """
        # Ensure the amount is not negative
        if amount < 0:
            raise ValueError("Amount to remove cannot be negative")
        # Check if there is enough stock
        if amount > self._quantity:
            raise InsufficientStockError(f"Not enough stock. Available: {self._quantity}, Requested: {amount}")
        self._quantity -= amount
        self._updated_at = datetime.now()
    
    # Step 2.7: String representations
    def __str__(self) -> str:
        """String representation of the product.
        Returns:
            A readable string for the product
        """
        return f"{self._name} (ID: {self._id}) - ${self._price:.2f} - Qty: {self._quantity}"
    
    def __repr__(self) -> str:
        """Official string representation of the product.
        Returns:
            A detailed string for debugging
        """
        return f"{self.__class__.__name__}(id='{self._id}', name='{self._name}', price={self._price}, quantity={self._quantity}, category='{self._category}')"
    
    # Step 2.8: Abstract method for displaying details
    @abstractmethod
    def display_details(self) -> Dict:
        """Abstract method to display product details.
        Subclasses must implement this to show type-specific details.
        Returns:
            A dictionary of product details
        """
        pass
    
    # Step 2.9: Convert product to dictionary for JSON
    def to_dict(self) -> Dict:
        """Convert product to dictionary for JSON serialization.
        Returns:
            A dictionary with product data
        """
        return {
            "id": self._id,
            "name": self._name,
            "price": self._price,
            "quantity": self._quantity,
            "category": self._category,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "type": self.__class__.__name__
        }
    
    # Step 2.10: Placeholder for creating a product from a dictionary
    @classmethod
    def from_dict(cls, data: Dict) -> 'Product':
        """Create a product from a dictionary.
        Subclasses implement this to recreate specific product types.
        Args:
            data: A dictionary with product data
        Returns:
            A Product object
        """
        pass


# Step 3: Define the PhysicalProduct class
class PhysicalProduct(Product):
    """Physical product with dimensions and weight.
    This represents tangible products like laptops or chairs.
    """
    
    # Step 3.1: Initialize a physical product
    def __init__(self, name: str, price: float, quantity: int, category: str, 
                 weight: float = 0.0, dimensions: Dict[str, float] = None):
        """Initialize a physical product.
        Args:
            name, price, quantity, category: Base product attributes
            weight: Weight in kg (default: 0.0)
            dimensions: Dictionary with length, width, height (default: 0,0,0)
        """
        # Call the parent Product class's __init__
        super().__init__(name, price, quantity, category)
        # Store weight and dimensions
        self._weight = weight
        self._dimensions = dimensions or {"length": 0, "width": 0, "height": 0}
    
    # Step 3.2: Properties for weight
    @property
    def weight(self) -> float:
        """Get the product weight.
        Returns:
            The weight in kg
        """
        return self._weight
    
    @weight.setter
    def weight(self, value: float) -> None:
        """Set the product weight.
        Args:
            value: The new weight
        """
        # Ensure weight is not negative
        if value < 0:
            raise ValueError("Weight cannot be negative")
        self._weight = float(value)
        self._updated_at = datetime.now()
    
    # Step 3.3: Properties for dimensions
    @property
    def dimensions(self) -> Dict[str, float]:
        """Get the product dimensions.
        Returns:
            A dictionary with length, width, height
        """
        return self._dimensions
    
    @dimensions.setter
    def dimensions(self, value: Dict[str, float]) -> None:
        """Set the product dimensions.
        Args:
            value: A dictionary with length, width, height
        """
        # Ensure all required keys are present
        required_keys = ["length", "width", "height"]
        if not all(k in value for k in required_keys):
            raise ValueError(f"Dimensions must include {', '.join(required_keys)}")
        # Ensure dimensions are not negative
        if any(v < 0 for v in value.values()):
            raise ValueError("Dimensions cannot be negative")
        self._dimensions = value
        self._updated_at = datetime.now()
    
    # Step 3.4: Display physical product details
    def display_details(self) -> Dict:
        """Display physical product details.
        Returns:
            A dictionary with product details, including weight and dimensions
        """
        basic_details = {
            "id": self._id,
            "name": self._name,
            "price": f"${self._price:.2f}",
            "quantity": self._quantity,
            "category": self._category,
            "value": f"${self.value:.2f}",
            "type": "Physical Product"
        }
        
        physical_details = {
            "weight": f"{self._weight} kg",
            "dimensions": f"{self._dimensions['length']}×{self._dimensions['width']}×{self._dimensions['height']} cm"
        }
        
        # Combine basic and physical details
        return {**basic_details, **physical_details}
    
    # Step 3.5: Convert to dictionary
    def to_dict(self) -> Dict:
        """Convert physical product to dictionary.
        Returns:
            A dictionary with all product data
        """
        data = super().to_dict()
        data.update({
            "weight": self._weight,
            "dimensions": self._dimensions
        })
        return data
    
    # Step 3.6: Create from dictionary
    @classmethod
    def from_dict(cls, data: Dict) -> 'PhysicalProduct':
        """Create a physical product from a dictionary.
        Args:
            data: A dictionary with product data
        Returns:
            A PhysicalProduct object
        """
        product = cls(
            name=data["name"],
            price=data["price"],
            quantity=data["quantity"],
            category=data["category"],
            weight=data.get("weight", 0.0),
            dimensions=data.get("dimensions", {"length": 0, "width": 0, "height": 0})
        )
        product._id = data["id"]
        product._created_at = datetime.fromisoformat(data["created_at"])
        product._updated_at = datetime.fromisoformat(data["updated_at"])
        return product


# Step 4: Define the DigitalProduct class
class DigitalProduct(Product):
    """Digital product with download link and file size.
    This represents digital items like software or e-books.
    """
    
    # Step 4.1: Initialize a digital product
    def __init__(self, name: str, price: float, quantity: int, category: str, 
                 file_size: float = 0.0, download_link: str = ""):
        """Initialize a digital product.
        Args:
            name, price, quantity, category: Base product attributes
            file_size: Size in MB (default: 0.0)
            download_link: URL for downloading (default: empty)
        """
        super().__init__(name, price, quantity, category)
        self._file_size = file_size
        self._download_link = download_link
    
    # Step 4.2: Properties for file size
    @property
    def file_size(self) -> float:
        """Get the file size.
        Returns:
            The file size in MB
        """
        return self._file_size
    
    @file_size.setter
    def file_size(self, value: float) -> None:
        """Set the file size.
        Args:
            value: The new file size
        """
        # Ensure file size is not negative
        if value < 0:
            raise ValueError("File size cannot be negative")
        self._file_size = float(value)
        self._updated_at = datetime.now()
    
    # Step 4.3: Properties for download link
    @property
    def download_link(self) -> str:
        """Get the download link.
        Returns:
            The download URL
        """
        return self._download_link
    
    @download_link.setter
    def download_link(self, value: str) -> None:
        """Set the download link.
        Args:
            value: The new download URL
        """
        self._download_link = value
        self._updated_at = datetime.now()
    
    # Step 4.4: Display digital product details
    def display_details(self) -> Dict:
        """Display digital product details.
        Returns:
            A dictionary with product details, including file size and download link
        """
        basic_details = {
            "id": self._id,
            "name": self._name,
            "price": f"${self._price:.2f}",
            "quantity": self._quantity,
            "category": self._category,
            "value": f"${self.value:.2f}",
            "type": "Digital Product"
        }
        
        digital_details = {
            "file_size": f"{self._file_size} MB",
            "download_link": self._download_link or "No link provided"
        }
        
        return {**basic_details, **digital_details}
    
    # Step 4.5: Convert to dictionary
    def to_dict(self) -> Dict:
        """Convert digital product to dictionary.
        Returns:
            A dictionary with all product data
        """
        data = super().to_dict()
        data.update({
            "file_size": self._file_size,
            "download_link": self._download_link
        })
        return data
    
    # Step 4.6: Create from dictionary
    @classmethod
    def from_dict(cls, data: Dict) -> 'DigitalProduct':
        """Create a digital product from a dictionary.
        Args:
            data: A dictionary with product data
        Returns:
            A DigitalProduct object
        """
        product = cls(
            name=data["name"],
            price=data["price"],
            quantity=data["quantity"],
            category=data["category"],
            file_size=data.get("file_size", 0.0),
            download_link=data.get("download_link", "")
        )
        product._id = data["id"]
        product._created_at = datetime.fromisoformat(data["created_at"])
        product._updated_at = datetime.fromisoformat(data["updated_at"])
        return product


# Step 5: Define the ServiceProduct class
class ServiceProduct(Product):
    """Service product with duration and service type.
    This represents services like consultations or repairs.
    """
    
    # Step 5.1: Initialize a service product
    def __init__(self, name: str, price: float, quantity: int, category: str, 
                 duration: int = 0, service_type: str = ""):
        """Initialize a service product.
        Args:
            name, price, quantity, category: Base product attributes
            duration: Service duration in minutes (default: 0)
            service_type: Type of service (default: empty)
        """
        super().__init__(name, price, quantity, category)
        self._duration = duration
        self._service_type = service_type
    
    # Step 5.2: Properties for duration
    @property
    def duration(self) -> int:
        """Get the service duration.
        Returns:
            The duration in minutes
        """
        return self._duration
    
    @duration.setter
    def duration(self, value: int) -> None:
        """Set the service duration.
        Args:
            value: The new duration
        """
        # Ensure duration is not negative
        if value < 0:
            raise ValueError("Duration cannot be negative")
        self._duration = int(value)
        self._updated_at = datetime.now()
    
    # Step 5.3: Properties for service type
    @property
    def service_type(self) -> str:
        """Get the service type.
        Returns:
            The type of service
        """
        return self._service_type
    
    @service_type.setter
    def service_type(self, value: str) -> None:
        """Set the service type.
        Args:
            value: The new service type
        """
        self._service_type = value
        self._updated_at = datetime.now()
    
    # Step 5.4: Display service product details
    def display_details(self) -> Dict:
        """Display service product details.
        Returns:
            A dictionary with product details, including duration and service type
        """
        basic_details = {
            "id": self._id,
            "name": self._name,
            "price": f"${self._price:.2f}",
            "quantity": self._quantity,
            "category": self._category,
            "value": f"${self.value:.2f}",
            "type": "Service Product"
        }
        
        service_details = {
            "duration": f"{self._duration} minutes",
            "service_type": self._service_type or "Standard"
        }
        
        return {**basic_details, **service_details}
    
    # Step 5.5: Convert to dictionary
    def to_dict(self) -> Dict:
        """Convert service product to dictionary.
        Returns:
            A dictionary with all product data
        """
        data = super().to_dict()
        data.update({
            "duration": self._duration,
            "service_type": self._service_type
        })
        return data
    
    # Step 5.6: Create from dictionary
    @classmethod
    def from_dict(cls, data: Dict) -> 'ServiceProduct':
        """Create a service product from a dictionary.
        Args:
            data: A dictionary with product data
        Returns:
            A ServiceProduct object
        """
        product = cls(
            name=data["name"],
            price=data["price"],
            quantity=data["quantity"],
            category=data["category"],
            duration=data.get("duration", 0),
            service_type=data.get("service_type", "")
        )
        product._id = data["id"]
        product._created_at = datetime.fromisoformat(data["created_at"])
        product._updated_at = datetime.fromisoformat(data["updated_at"])
        return product


# Step 6: Define custom exceptions
class InsufficientStockError(Exception):
    """Exception raised when trying to remove more stock than available."""
    # Used when there isn't enough stock to fulfill a request
    pass


class ProductNotFoundError(Exception):
    """Exception raised when a product is not found."""
    # Used when a product ID doesn't exist
    pass


class DuplicateProductError(Exception):
    """Exception raised when attempting to add a product with an existing ID."""
    # Used when trying to add a product with an ID already in use
    pass
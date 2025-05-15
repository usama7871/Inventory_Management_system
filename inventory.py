"""
Inventory and InventoryManager classes for the Inventory Management System.
This file manages the collection of products and saves/loads them to/from a JSON file.
"""

# Step 1: Import necessary libraries and classes
# - json: For reading/writing product data to a JSON file
# - os: For checking if files exist
# - typing: For type hints
# - streamlit: For displaying errors
# - product: Import product classes and exceptions from product.py
import json
import os
from typing import Dict, List
import streamlit as st
from product import Product, PhysicalProduct, DigitalProduct, ServiceProduct, ProductNotFoundError, DuplicateProductError


# Step 2: Define the Inventory class to manage products
class Inventory:
    """Manages a collection of products.
    This class stores products in a dictionary and provides methods to add, remove, and search them.
    """
    
    # Step 2.1: Initialize an empty inventory
    def __init__(self):
        """Initialize an empty inventory."""
        # Create an empty dictionary to store products (key: product ID, value: Product object)
        self._products: Dict[str, Product] = {}
    
    # Step 2.2: Property to get all products
    @property
    def products(self) -> Dict[str, Product]:
        """Get all products.
        Returns:
            The dictionary of products
        """
        return self._products
    
    # Step 2.3: Add a product to the inventory
    def add_product(self, product: Product) -> None:
        """Add a product to the inventory.
        Args:
            product: The Product object to add
        """
        # Check if the product ID already exists
        if product.id in self._products:
            raise DuplicateProductError(f"Product with ID {product.id} already exists")
        # Add the product to the dictionary
        self._products[product.id] = product
    
    # Step 2.4: Remove a product by ID
    def remove_product(self, product_id: str) -> None:
        """Remove a product from the inventory.
        Args:
            product_id: The ID of the product to remove
        """
        # Check if the product exists
        if product_id not in self._products:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
        # Remove the product from the dictionary
        del self._products[product_id]
    
    # Step 2.5: Get a product by ID
    def get_product(self, product_id: str) -> Product:
        """Get a product by ID.
        Args:
            product_id: The ID of the product
        Returns:
            The Product object
        """
        # Check if the product exists
        if product_id not in self._products:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
        return self._products[product_id]
    
    # Step 2.6: Update a product's attributes
    def update_product(self, product_id: str, **kwargs) -> None:
        """Update a product's attributes.
        Args:
            product_id: The ID of the product
            **kwargs: Key-value pairs of attributes to update (e.g., name="New Name")
        """
        # Get the product
        product = self.get_product(product_id)
        
        # Update each provided attribute
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
            else:
                raise AttributeError(f"Product has no attribute '{key}'")
    
    # Step 2.7: Search products by name
    def search_by_name(self, name: str) -> List[Product]:
        """Search products by name (case-insensitive).
        Args:
            name: The name to search for
        Returns:
            A list of matching Product objects
        """
        name = name.lower()
        # Return products where the search term is in the product name
        return [p for p in self._products.values() if name in p.name.lower()]
    
    # Step 2.8: Search products by category
    def search_by_category(self, category: str) -> List[Product]:
        """Search products by category (case-insensitive).
        Args:
            category: The category to search for
        Returns:
            A list of matching Product objects
        """
        category = category.lower()
        # Return products where the search term is in the category
        return [p for p in self._products.values() if category in p.category.lower()]
    
    # Step 2.9: Get products with low stock
    def get_low_stock_products(self, threshold: int = 5) -> List[Product]:
        """Get products with stock below the given threshold.
        Args:
            threshold: The stock level to check (default: 5)
        Returns:
            A list of Product objects with low stock
        """
        # Return products with quantity <= threshold
        return [p for p in self._products.values() if p.quantity <= threshold]
    
    # Step 2.10: Calculate the total value of the inventory
    def get_total_value(self) -> float:
        """Calculate the total value of all products in the inventory.
        Returns:
            The sum of (price * quantity) for all products
        """
        return sum(p.value for p in self._products.values())
    
    # Step 2.11: Count products by type
    def get_count_by_type(self) -> Dict[str, int]:
        """Count products by their type.
        Returns:
            A dictionary with product types and their counts
        """
        type_counts = {}
        # Count each product by its class name (e.g., PhysicalProduct)
        for product in self._products.values():
            product_type = product.__class__.__name__
            type_counts[product_type] = type_counts.get(product_type, 0) + 1
        return type_counts
    
    # Step 2.12: Clear all products
    def clear(self) -> None:
        """Clear all products from the inventory."""
        self._products.clear()


# Step 3: Define the InventoryManager class to handle persistence
class InventoryManager:
    """Manages inventory persistence and operations.
    This class saves and loads the inventory to/from a JSON file and manages operations.
    """
    
    # Step 3.1: Initialize the InventoryManager
    def __init__(self, file_path: str = "inventory_data.json"):
        """Initialize the inventory manager.
        Args:
            file_path: The file where inventory data is stored (default: 'inventory_data.json')
        """
        # Store the path to the inventory data file
        self.file_path = file_path
        # Create a new Inventory object
        self.inventory = Inventory()
        # Load existing inventory data from the JSON file
        self._load_data()
    
    # Step 3.2: Load inventory data from the JSON file
    def _load_data(self) -> None:
        """Load inventory data from JSON file.
        This reads the inventory_data.json file and loads products into the inventory.
        """
        # Check if the file exists
        if not os.path.exists(self.file_path):
            return
        
        try:
            # Open and read the JSON file
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                
                # Clear the current inventory
                self.inventory.clear()
                
                # Convert each product dictionary into the appropriate Product object
                for item in data:
                    product_type = item.get("type")
                    
                    if product_type == "PhysicalProduct":
                        product = PhysicalProduct.from_dict(item)
                    elif product_type == "DigitalProduct":
                        product = DigitalProduct.from_dict(item)
                    elif product_type == "ServiceProduct":
                        product = ServiceProduct.from_dict(item)
                    else:
                        continue
                    
                    # Add the product to the inventory
                    self.inventory.add_product(product)
        except (json.JSONDecodeError, IOError) as e:
            # Show an error in the Streamlit app if loading fails
            st.error(f"Error loading inventory data: {str(e)}")
    
    # Step 3.3: Save inventory data to the JSON file
    def save_data(self) -> None:
        """Save inventory data to JSON file.
        This writes all products to the inventory_data.json file.
        """
        try:
            # Convert all Product objects to dictionaries
            data = [p.to_dict() for p in self.inventory.products.values()]
            
            # Write the data to the JSON file
            with open(self.file_path, 'w') as file:
                json.dump(data, file, indent=4)
        except IOError as e:
            # Show an error in the Streamlit app if saving fails
            st.error(f"Error saving inventory data: {str(e)}")
    
    # Step 3.4: Add a product and save
    def add_product(self, product: Product) -> None:
        """Add a product and save.
        Args:
            product: The Product object to add
        """
        # Add the product to the inventory
        self.inventory.add_product(product)
        # Save the updated inventory
        self.save_data()
    
    # Step 3.5: Remove a product and save
    def remove_product(self, product_id: str) -> None:
        """Remove a product and save.
        Args:
            product_id: The ID of the product to remove
        """
        # Remove the product from the inventory
        self.inventory.remove_product(product_id)
        # Save the updated inventory
        self.save_data()
    
    # Step 3.6: Update a product and save
    def update_product(self, product_id: str, **kwargs) -> None:
        """Update a product and save.
        Args:
            product_id: The ID of the product
            **kwargs: Attributes to update
        """
        # Update the product in the inventory
        self.inventory.update_product(product_id, **kwargs)
        # Save the updated inventory
        self.save_data()
    
    # Step 3.7: Add stock to a product and save
    def add_stock(self, product_id: str, amount: int) -> None:
        """Add stock to a product and save.
        Args:
            product_id: The ID of the product
            amount: The amount to add
        """
        # Get the product and add stock
        product = self.inventory.get_product(product_id)
        product.add_stock(amount)
        # Save the updated inventory
        self.save_data()
    
    # Step 3.8: Remove stock from a product and save
    def remove_stock(self, product_id: str, amount: int) -> None:
        """Remove stock from a product and save.
        Args:
            product_id: The ID of the product
            amount: The amount to remove
        """
        # Get the product and remove stock
        product = self.inventory.get_product(product_id)
        product.remove_stock(amount)
        # Save the updated inventory
        self.save_data()
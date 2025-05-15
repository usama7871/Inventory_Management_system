"""
User authentication classes for the Inventory Management System.
This file handles user login, password management, and saving user data.
"""

# Step 1: Import necessary libraries
# - json: For reading/writing user data to a JSON file
# - os: For checking if files exist
# - typing: For type hints to make code clearer
# - streamlit: For displaying errors in the web app
# - hashlib: For creating secure password hashes
import json
import os
from typing import Dict, Optional
import streamlit as st
import hashlib


# Step 2: Define a custom exception for authentication errors
class AuthenticationError(Exception):
    """Exception raised for authentication issues, like wrong username/password."""
    # This class is used to signal login problems
    pass


# Step 3: Define the User class to represent a single user
class User:
    """User class for authentication.
    This class stores a user's username, password (as a hash), and role (e.g., admin or user).
    """
    
    # Step 3.1: Initialize a user with username, password, and role
    def __init__(self, username: str, password: str, role: str = "user"):
        """Initialize a user.
        Args:
            username: The user's unique name
            password: The user's password (will be hashed for security)
            role: The user's role (defaults to 'user')
        """
        # Store the username directly
        self.username = username
        # Hash the password for secure storage
        self._password_hash = self._hash_password(password)
        # Store the role (e.g., 'admin' or 'user')
        self.role = role
    
    # Step 3.2: Create a method to hash passwords
    def _hash_password(self, password: str) -> str:
        """Simple password hashing (in a real app, use a proper hashing library).
        This turns a password into a secure code (hash) so we don't store plain text.
        Args:
            password: The plain text password
        Returns:
            A hashed version of the password
        """
        # Use SHA-256 to create a secure hash of the password
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Step 3.3: Verify if a provided password matches the stored hash
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash.
        Args:
            password: The password to check
        Returns:
            True if the password matches, False otherwise
        """
        # Hash the provided password and compare it to the stored hash
        hashed = self._hash_password(password)
        return hashed == self._password_hash
    
    # Step 3.4: Convert user data to a dictionary for saving to JSON
    def to_dict(self) -> Dict:
        """Convert user to dictionary.
        This prepares user data to be saved in a JSON file.
        Returns:
            A dictionary with username, password hash, and role
        """
        return {
            "username": self.username,
            "password_hash": self._password_hash,
            "role": self.role
        }
    
    # Step 3.5: Create a user from a dictionary (used when loading from JSON)
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create a user from a dictionary.
        This is used to recreate a User object from saved JSON data.
        Args:
            data: A dictionary with user data
        Returns:
            A User object
        """
        # Create a new User object without calling __init__
        user = cls.__new__(cls)
        # Set the username, password hash, and role directly
        user.username = data["username"]
        user._password_hash = data["password_hash"]
        user.role = data.get("role", "user")
        return user


# Step 4: Define the UserManager class to handle multiple users
class UserManager:
    """Manages user authentication and persistence.
    This class loads, saves, and manages all users in the system.
    """
    
    # Step 4.1: Initialize the UserManager
    def __init__(self, file_path: str = "user_data.json"):
        """Initialize the user manager.
        Args:
            file_path: The file where user data is stored (default: 'user_data.json')
        """
        # Store the path to the user data file
        self.file_path = file_path
        # Create an empty dictionary to store users (key: username, value: User object)
        self.users: Dict[str, User] = {}
        # Load existing user data from the JSON file
        self._load_data()
        
        # If no users exist, create a default admin user
        if not self.users:
            self.add_user(User("admin", "admin123", "admin"))
    
    # Step 4.2: Load user data from the JSON file
    def _load_data(self) -> None:
        """Load user data from JSON file.
        This reads the user_data.json file and loads users into the self.users dictionary.
        """
        # Check if the file exists
        if not os.path.exists(self.file_path):
            return
        
        try:
            # Open and read the JSON file
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                
                # Clear the current users dictionary
                self.users.clear()
                
                # Convert each user dictionary into a User object
                for username, user_data in data.items():
                    self.users[username] = User.from_dict(user_data)
        except (json.JSONDecodeError, IOError) as e:
            # Show an error in the Streamlit app if loading fails
            st.error(f"Error loading user data: {str(e)}")
    
    # Step 4.3: Save user data to the JSON file
    def save_data(self) -> None:
        """Save user data to JSON file.
        This writes all users to the user_data.json file.
        """
        try:
            # Convert all User objects to dictionaries
            data = {username: user.to_dict() for username, user in self.users.items()}
            
            # Write the data to the JSON file
            with open(self.file_path, 'w') as file:
                json.dump(data, file, indent=4)
        except IOError as e:
            # Show an error in the Streamlit app if saving fails
            st.error(f"Error saving user data: {str(e)}")
    
    # Step 4.4: Add a new user
    def add_user(self, user: User) -> None:
        """Add a user and save.
        Args:
            user: The User object to add
        """
        # Check if the username already exists
        if user.username in self.users:
            raise ValueError(f"User '{user.username}' already exists")
        # Add the user to the dictionary
        self.users[user.username] = user
        # Save the updated user list to the JSON file
        self.save_data()
    
    # Step 4.5: Authenticate a user during login
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user.
        Args:
            username: The username to check
            password: The password to verify
        Returns:
            The User object if authentication succeeds, None otherwise
        """
        # Check if the username exists
        if username not in self.users:
            return None
        
        # Get the user and verify the password
        user = self.users[username]
        if user.verify_password(password):
            return user
        return None
    
    # Step 4.6: Change a user's password
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change a user's password.
        Args:
            username: The username of the user
            old_password: The current password
            new_password: The new password
        Returns:
            True if the password was changed, False if authentication failed
        """
        # Verify the old password
        user = self.authenticate(username, old_password)
        if not user:
            return False
        
        # Create a new User object with the new password
        new_user = User(username, new_password, user.role)
        # Update the user in the dictionary
        self.users[username] = new_user
        # Save the updated user list
        self.save_data()
        return True
"""
Streamlit UI for the Inventory Management System.
This file creates the web interface for users to interact with the inventory system.
"""

# Step 1: Import necessary libraries and classes
# - streamlit: For building the web interface
# - json: For handling JSON data (export/import)
# - inventory: For managing the product inventory
# - product: For creating different types of products
# - auth: For handling user authentication
import streamlit as st
import json
from inventory import InventoryManager, ProductNotFoundError
from product import PhysicalProduct, DigitalProduct, ServiceProduct
from auth import User, UserManager, AuthenticationError


# Step 2: Define the login page function
def login_page():
    """Display the login page.
    This is the first page users see to log in or sign up.
    """
    # Step 2.1: Set the page title
    st.title("📦 Inventory Management System")
    
    # Step 2.2: Create a form for login/signup
    with st.form("login_form"):
        # Add input fields for username and password
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        # Create two columns for buttons
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login")
        with col2:
            signup_button = st.form_submit_button("Sign Up")
    
    # Step 2.3: Create a UserManager to handle authentication
    user_manager = UserManager()
    
    # Step 2.4: Handle login button click
    if login_button:
        # Check if username or password is empty
        if not username or not password:
            st.error("Please enter both username and password")
            return None
        
        # Try to authenticate the user
        user = user_manager.authenticate(username, password)
        if user:
            # Store user info in session state to keep them logged in
            st.session_state.user = user
            st.session_state.username = username
            st.session_state.role = user.role
            st.session_state.authenticated = True
            # Refresh the app to show the main interface
            st.rerun()
        else:
            st.error("Invalid username or password")
    
    # Step 2.5: Handle signup button click
    if signup_button:
        # Check if username or password is empty
        if not username or not password:
            st.error("Please enter both username and password")
            return None
        
        # Check if the username already exists
        if username in user_manager.users:
            st.error("Username already exists")
            return None
        
        try:
            # Create a new user and add them to the system
            user = User(username, password, "user")
            user_manager.add_user(user)
            st.success("Account created successfully! You can now log in.")
        except Exception as e:
            st.error(f"Error creating account: {str(e)}")


# Step 3: Define the sidebar menu function
def sidebar_menu():
    """Display the sidebar menu.
    This shows navigation options and user info after login.
    """
    with st.sidebar:
        # Step 3.1: Show the sidebar title
        st.title("Navigation")
        
        # Step 3.2: Display the logged-in user's info
        st.write(f"Logged in as: **{st.session_state.username}**")
        st.write(f"Role: **{st.session_state.role}**")
        
        # Step 3.3: Show the menu options
        st.subheader("Menu")
        page = st.radio(
            "Select a page:",
            [
                "Dashboard",
                "Products",
                "Add Product",
                "Search",
                "Stock Management",
                "Settings"
            ],
            index=0
        )
        
        # Step 3.4: Handle logout button
        if st.button("Logout"):
            # Clear all session state data
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Refresh the app to show the login page
            st.rerun()
    
    # Return the selected page
    return page


# Step 4: Define the dashboard page function
def dashboard_page(inventory_manager: InventoryManager):
    """Display the dashboard page.
    This shows an overview of the inventory with key metrics.
    Args:
        inventory_manager: The InventoryManager object to access products
    """
    # Step 4.1: Set the page title
    st.title("Dashboard")
    
    # Step 4.2: Create three columns for metrics
    col1, col2, col3 = st.columns(3)
    
    # Step 4.3: Show total products
    with col1:
        st.metric(
            "Total Products", 
            len(inventory_manager.inventory.products)
        )
    
    # Step 4.4: Show total inventory value
    with col2:
        total_value = inventory_manager.inventory.get_total_value()
        st.metric(
            "Total Inventory Value", 
            f"${total_value:.2f}"
        )
    
    # Step 4.5: Show low stock items
    with col3:
        low_stock = len(inventory_manager.inventory.get_low_stock_products())
        st.metric(
            "Low Stock Items", 
            low_stock,
            delta="Needs attention" if low_stock > 0 else "All good"
        )
    
    # Step 4.6: Show product distribution chart
    st.subheader("Product Distribution")
    type_counts = inventory_manager.inventory.get_count_by_type()
    
    if type_counts:
        # Create data for the bar chart
        chart_data = {
            "Type": list(type_counts.keys()),
            "Count": list(type_counts.values())
        }
        st.bar_chart(chart_data, x="Type", y="Count")
    else:
        st.info("No products in inventory yet.")
    
    # Step 4.7: Show low stock warnings
    low_stock_products = inventory_manager.inventory.get_low_stock_products()
    if low_stock_products:
        st.subheader("Low Stock Warning")
        for product in low_stock_products:
            st.warning(f"{product.name} - Only {product.quantity} left in stock")


# Step 5: Define the products page function
def products_page(inventory_manager: InventoryManager):
    """Display the products page.
    This lists all products with filtering and sorting options.
    Args:
        inventory_manager: The InventoryManager object to access products
    """
    # Step 5.1: Set the page title
    st.title("Products")
    
    # Step 5.2: Show filter options
    st.subheader("Filter Options")
    col1, col2 = st.columns(2)
    
    with col1:
        # Get unique categories for filtering
        filter_category = st.selectbox(
            "Filter by Category",
            ["All"] + list(set(p.category for p in inventory_manager.inventory.products.values())),
            index=0
        )
    
    with col2:
        # Filter by product type
        filter_type = st.selectbox(
            "Filter by Type",
            ["All", "PhysicalProduct", "DigitalProduct", "ServiceProduct"],
            index=0
        )
    
    # Step 5.3: Filter products based on user selection
    filtered_products = list(inventory_manager.inventory.products.values())
    
    if filter_category != "All":
        filtered_products = [p for p in filtered_products if p.category == filter_category]
    
    if filter_type != "All":
        filtered_products = [p for p in filtered_products if p.__class__.__name__ == filter_type]
    
    # Step 5.4: Check if any products match the filters
    if not filtered_products:
        st.info("No products match your filter criteria.")
        return
    
    # Step 5.5: Add sorting options
    sort_option = st.selectbox(
        "Sort by",
        ["Name (A-Z)", "Name (Z-A)", "Price (Low to High)", "Price (High to Low)", 
         "Quantity (Low to High)", "Quantity (High to Low)"],
        index=0
    )
    
    # Step 5.6: Sort products based on user selection
    if sort_option == "Name (A-Z)":
        filtered_products.sort(key=lambda p: p.name)
    elif sort_option == "Name (Z-A)":
        filtered_products.sort(key=lambda p: p.name, reverse=True)
    elif sort_option == "Price (Low to High)":
        filtered_products.sort(key=lambda p: p.price)
    elif sort_option == "Price (High to Low)":
        filtered_products.sort(key=lambda p: p.price, reverse=True)
    elif sort_option == "Quantity (Low to High)":
        filtered_products.sort(key=lambda p: p.quantity)
    elif sort_option == "Quantity (High to Low)":
        filtered_products.sort(key=lambda p: p.quantity, reverse=True)
    
    # Step 5.7: Display each product
    for i, product in enumerate(filtered_products):
        with st.expander(f"{product.name} - ${product.price:.2f} - Qty: {product.quantity}"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Show an icon based on product type
                if isinstance(product, PhysicalProduct):
                    st.markdown("### 📦")
                elif isinstance(product, DigitalProduct):
                    st.markdown("### 💻")
                elif isinstance(product, ServiceProduct):
                    st.markdown("### 🛠️")
                
                st.write(f"**ID:** {product.id}")
                st.write(f"**Type:** {product.__class__.__name__}")
            
            with col2:
                # Show product details
                for key, value in product.display_details().items():
                    if key not in ["id", "type"]:
                        st.write(f"**{key.capitalize()}:** {value}")
            
            # Step 5.8: Add action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"Edit #{product.id}", key=f"edit_{product.id}"):
                    st.session_state.edit_product_id = product.id
                    st.rerun()
            
            with col2:
                if st.button(f"Add Stock #{product.id}", key=f"add_stock_{product.id}"):
                    st.session_state.stock_product_id = product.id
                    st.session_state.stock_action = "add"
                    st.rerun()
            
            with col3:
                if st.button(f"Remove #{product.id}", key=f"remove_{product.id}"):
                    try:
                        inventory_manager.remove_product(product.id)
                        st.success(f"Product '{product.name}' removed successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error removing product: {str(e)}")


# Step 6: Define the add product page function
def add_product_page(inventory_manager: InventoryManager):
    """Display the add product page.
    This allows users to add a new product to the inventory.
    Args:
        inventory_manager: The InventoryManager object to add products
    """
    # Step 6.1: Set the page title
    st.title("Add New Product")
    
    # Step 6.2: Select product type
    product_type = st.selectbox(
        "Product Type",
        ["Physical Product", "Digital Product", "Service Product"],
        index=0
    )
    
    # Step 6.3: Create a form for adding the product
    with st.form(f"add_{product_type}_form"):
        name = st.text_input("Product Name")
        
        col1, col2 = st.columns(2)
        with col1:
            price = st.number_input("Price ($)", min_value=0.0, value=0.0, step=0.01)
        with col2:
            quantity = st.number_input("Initial Quantity", min_value=0, value=0, step=1)
        
        category = st.text_input("Category")
        
        # Step 6.4: Add type-specific fields
        if product_type == "Physical Product":
            weight = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.1)
            
            st.subheader("Dimensions (cm)")
            dim_col1, dim_col2, dim_col3 = st.columns(3)
            with dim_col1:
                length = st.number_input("Length", min_value=0.0, value=0.0, step=0.1)
            with dim_col2:
                width = st.number_input("Width", min_value=0.0, value=0.0, step=0.1)
            with dim_col3:
                height = st.number_input("Height", min_value=0.0, value=0.0, step=0.1)
        
        elif product_type == "Digital Product":
            file_size = st.number_input("File Size (MB)", min_value=0.0, value=0.0, step=0.1)
            download_link = st.text_input("Download Link")
        
        elif product_type == "Service Product":
            duration = st.number_input("Duration (minutes)", min_value=0, value=0, step=5)
            service_type = st.text_input("Service Type")
        
        submit_button = st.form_submit_button("Add Product")
    
    # Step 6.5: Handle form submission
    if submit_button:
        try:
            # Validate required fields
            if not name or not category:
                st.error("Product name and category are required")
                return
            
            # Create the appropriate product object
            if product_type == "Physical Product":
                dimensions = {"length": length, "width": width, "height": height}
                product = PhysicalProduct(name, price, quantity, category, weight, dimensions)
            
            elif product_type == "Digital Product":
                product = DigitalProduct(name, price, quantity, category, file_size, download_link)
            
            elif product_type == "Service Product":
                product = ServiceProduct(name, price, quantity, category, duration, service_type)
            
            # Add the product to the inventory
            inventory_manager.add_product(product)
            st.success(f"Product '{name}' added successfully with ID: {product.id}")
            
            st.rerun()
        
        except Exception as e:
            st.error(f"Error adding product: {str(e)}")


# Step 7: Define the search page function
def search_page(inventory_manager: InventoryManager):
    """Display the search page.
    This allows users to search for products by name, category, or ID.
    Args:
        inventory_manager: The InventoryManager object to search products
    """
    # Step 7.1: Set the page title
    st.title("Search Products")
    
    # Step 7.2: Select search type
    search_type = st.radio(
        "Search by:",
        ["Name", "Category", "ID"],
        horizontal=True
    )
    
    # Step 7.3: Get search term
    search_term = st.text_input("Enter search term")
    
    # Step 7.4: Handle search
    if search_term:
        try:
            if search_type == "Name":
                results = inventory_manager.inventory.search_by_name(search_term)
                st.write(f"Found {len(results)} products matching '{search_term}'")
            
            elif search_type == "Category":
                results = inventory_manager.inventory.search_by_category(search_term)
                st.write(f"Found {len(results)} products in category '{search_term}'")
            
            elif search_type == "ID":
                try:
                    product = inventory_manager.inventory.get_product(search_term)
                    results = [product]
                    st.write(f"Found product with ID '{search_term}'")
                except ProductNotFoundError:
                    results = []
                    st.warning(f"No product found with ID '{search_term}'")
            
            # Step 7.5: Display search results
            if results:
                st.subheader("Search Results")
                
                for product in results:
                    with st.expander(f"{product.name} ({product.__class__.__name__})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**ID:** {product.id}")
                            st.write(f"**Price:** ${product.price:.2f}")
                            st.write(f"**Quantity:** {product.quantity}")
                            st.write(f"**Category:** {product.category}")
                        
                        with col2:
                            # Show type-specific details
                            if isinstance(product, PhysicalProduct):
                                st.write(f"**Weight:** {product.weight} kg")
                                dims = product.dimensions
                                st.write(f"**Dimensions:** {dims['length']}×{dims['width']}×{dims['height']} cm")
                            
                            elif isinstance(product, DigitalProduct):
                                st.write(f"**File Size:** {product.file_size} MB")
                                if product.download_link:
                                    st.write(f"**Download Link:** {product.download_link}")
                            
                            elif isinstance(product, ServiceProduct):
                                st.write(f"**Duration:** {product.duration} minutes")
                                if product.service_type:
                                    st.write(f"**Service Type:** {product.service_type}")
                        
                        # Add action buttons
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(f"Edit #{product.id}", key=f"search_edit_{product.id}"):
                                st.session_state.edit_product_id = product.id
                                st.rerun()
                        
                        with col2:
                            if st.button(f"Add Stock #{product.id}", key=f"search_add_stock_{product.id}"):
                                st.session_state.stock_product_id = product.id
                                st.session_state.stock_action = "add"
                                st.rerun()
                        
                        with col3:
                            if st.button(f"Remove #{product.id}", key=f"search_remove_{product.id}"):
                                try:
                                    inventory_manager.remove_product(product.id)
                                    st.success(f"Product '{product.name}' removed successfully")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error removing product: {str(e)}")
            else:
                st.info("No products found matching your search criteria.")
        
        except Exception as e:
            st.error(f"Error during search: {str(e)}")


# Step 8: Define the stock management page function
def stock_management_page(inventory_manager: InventoryManager):
    """Display the stock management page.
    This allows users to add or remove stock for products.
    Args:
        inventory_manager: The InventoryManager object to manage stock
    """
    # Step 8.1: Set the page title
    st.title("Stock Management")
    
    # Step 8.2: Handle stock adjustment form
    if hasattr(st.session_state, 'stock_product_id') and hasattr(st.session_state, 'stock_action'):
        product_id = st.session_state.stock_product_id
        action = st.session_state.stock_action
        
        try:
            product = inventory_manager.inventory.get_product(product_id)
            
            st.subheader(f"{action.capitalize()} Stock for {product.name}")
            
            with st.form(f"{action}_stock_form"):
                amount = st.number_input(
                    f"Amount to {action}",
                    min_value=1,
                    value=1,
                    step=1
                )
                
                submit = st.form_submit_button(f"{action.capitalize()} Stock")
                cancel = st.form_submit_button("Cancel")
            
            if submit:
                try:
                    if action == "add":
                        inventory_manager.add_stock(product_id, amount)
                        st.success(f"Successfully added {amount} units to '{product.name}'")
                    elif action == "remove":
                        inventory_manager.remove_stock(product_id, amount)
                        st.success(f"Successfully removed {amount} units from '{product.name}'")
                    
                    del st.session_state.stock_product_id
                    del st.session_state.stock_action
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            
            if cancel:
                del st.session_state.stock_product_id
                del st.session_state.stock_action
                st.rerun()
        
        except ProductNotFoundError:
            st.error(f"Product with ID {product_id} not found.")
            del st.session_state.stock_product_id
            del st.session_state.stock_action
            st.rerun()
    
    else:
        # Step 8.3: Show low stock products
        low_stock = inventory_manager.inventory.get_low_stock_products()
        if low_stock:
            st.warning(f"You have {len(low_stock)} products with low stock!")
            
            for product in low_stock:
                with st.expander(f"{product.name} - Only {product.quantity} left"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {product.id}")
                        st.write(f"**Category:** {product.category}")
                        st.write(f"**Price:** ${product.price:.2f}")
                    
                    with col2:
                        if st.button(f"Add Stock #{product.id}", key=f"low_add_{product.id}"):
                            st.session_state.stock_product_id = product.id
                            st.session_state.stock_action = "add"
                            st.rerun()
        
        # Step 8.4: Show bulk stock management
        st.subheader("Bulk Stock Management")
        
        categories = ["All"] + list(set(p.category for p in inventory_manager.inventory.products.values()))
        selected_category = st.selectbox("Filter by Category", categories)
        
        if selected_category == "All":
            products = list(inventory_manager.inventory.products.values())
        else:
            products = [p for p in inventory_manager.inventory.products.values() if p.category == selected_category]
        
        if not products:
            st.info("No products found in the selected category.")
            return
        
        for product in products:
            with st.expander(f"{product.name} - Current stock: {product.quantity}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**ID:** {product.id}")
                    st.write(f"**Price:** ${product.price:.2f}")
                
                with col2:
                    if st.button(f"Add Stock", key=f"bulk_add_{product.id}"):
                        st.session_state.stock_product_id = product.id
                        st.session_state.stock_action = "add"
                        st.rerun()
                
                with col3:
                    if st.button(f"Remove Stock", key=f"bulk_remove_{product.id}"):
                        st.session_state.stock_product_id = product.id
                        st.session_state.stock_action = "remove"
                        st.rerun()


# Step 9: Define the settings page function
def settings_page(inventory_manager: InventoryManager):
    """Display the settings page.
    This allows users to manage their account and import/export data.
    Args:
        inventory_manager: The InventoryManager object to manage data
    """
    # Step 9.1: Set the page title
    st.title("Settings")
    
    # Step 9.2: User settings section
    st.subheader("User Settings")
    
    # Step 9.3: Admin-only user management
    if st.session_state.role == "admin":
        with st.expander("User Management"):
            user_manager = UserManager()
            
            st.write("### Existing Users")
            for username, user in user_manager.users.items():
                st.write(f"**Username:** {username} | **Role:** {user.role}")
            
            st.write("### Add New User")
            with st.form("add_user_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["user", "manager", "admin"])
                
                submit_user = st.form_submit_button("Add User")
            
            if submit_user:
                if not new_username or not new_password:
                    st.error("Username and password are required")
                elif new_username in user_manager.users:
                    st.error(f"User '{new_username}' already exists")
                else:
                    try:
                        user = User(new_username, new_password, new_role)
                        user_manager.add_user(user)
                        st.success(f"User '{new_username}' added successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding user: {str(e)}")
    
    # Step 9.4: Change password section
    with st.expander("Change Password"):
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            submit_password = st.form_submit_button("Change Password")
        
        if submit_password:
            if not current_password or not new_password or not confirm_password:
                st.error("All fields are required")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            else:
                user_manager = UserManager()
                if user_manager.change_password(st.session_state.username, current_password, new_password):
                    st.success("Password changed successfully")
                else:
                    st.error("Current password is incorrect")
    
    # Step 9.5: Application settings section
    st.subheader("Application Settings")
    
    # Step 9.6: Export data section
    with st.expander("Export Data"):
        if st.button("Export Inventory Data to JSON"):
            data = [p.to_dict() for p in inventory_manager.inventory.products.values()]
            json_data = json.dumps(data, indent=4)
            
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="inventory_export.json",
                mime="application/json"
            )
    
    # Step 9.7: Import data section
    with st.expander("Import Data"):
        uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
        
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                
                st.warning("Importing will replace all existing inventory data. Continue?")
                if st.button("Import Data"):
                    inventory_manager.inventory.clear()
                    
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
                        
                        inventory_manager.inventory.add_product(product)
                    
                    inventory_manager.save_data()
                    st.success("Data imported successfully")
                    st.rerun()
            except json.JSONDecodeError:
                st.error("Invalid JSON file")
            except Exception as e:
                st.error(f"Error importing data: {str(e)}")
    
    # Step 9.8: Admin-only clear data section
    if st.session_state.role == "admin":
        with st.expander("Clear Data"):
            st.warning("This will delete all products from the inventory. This action cannot be undone.")
            if st.button("Clear All Inventory Data"):
                inventory_manager.inventory.clear()
                inventory_manager.save_data()
                st.success("All inventory data has been cleared")
                st.rerun()


# Step 10: Define the edit product page function
def edit_product_page(inventory_manager: InventoryManager):
    """Display the edit product page.
    This allows users to edit an existing product's details.
    Args:
        inventory_manager: The InventoryManager object to update products
    """
    # Step 10.1: Set the page title
    st.title("Edit Product")
    
    # Step 10.2: Get the product ID to edit
    product_id = st.session_state.edit_product_id
    
    try:
        product = inventory_manager.inventory.get_product(product_id)
        
        # Step 10.3: Create a form for editing
        with st.form("edit_product_form"):
            st.write(f"Editing: **{product.name}** (ID: {product.id})")
            
            name = st.text_input("Product Name", value=product.name)
            
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Price ($)", min_value=0.0, value=product.price, step=0.01)
            with col2:
                quantity = st.number_input("Quantity", min_value=0, value=product.quantity, step=1)
            
            category = st.text_input("Category", value=product.category)
            
            # Step 10.4: Add type-specific fields
            if isinstance(product, PhysicalProduct):
                weight = st.number_input("Weight (kg)", min_value=0.0, value=product.weight, step=0.1)
                
                st.subheader("Dimensions (cm)")
                dims = product.dimensions
                dim_col1, dim_col2, dim_col3 = st.columns(3)
                with dim_col1:
                    length = st.number_input("Length", min_value=0.0, value=dims["length"], step=0.1)
                with dim_col2:
                    width = st.number_input("Width", min_value=0.0, value=dims["width"], step=0.1)
                with dim_col3:
                    height = st.number_input("Height", min_value=0.0, value=dims["height"], step=0.1)
            
            elif isinstance(product, DigitalProduct):
                file_size = st.number_input("File Size (MB)", min_value=0.0, value=product.file_size, step=0.1)
                download_link = st.text_input("Download Link", value=product.download_link)
            
            elif isinstance(product, ServiceProduct):
                duration = st.number_input("Duration (minutes)", min_value=0, value=product.duration, step=5)
                service_type = st.text_input("Service Type", value=product.service_type)
            
            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("Save Changes")
            with col2:
                cancel_button = st.form_submit_button("Cancel")
        
        # Step 10.5: Handle form submission
        if submit_button:
            try:
                updates = {
                    "name": name,
                    "price": price,
                    "quantity": quantity,
                    "category": category
                }
                
                if isinstance(product, PhysicalProduct):
                    updates["weight"] = weight
                    updates["dimensions"] = {"length": length, "width": width, "height": height}
                
                elif isinstance(product, DigitalProduct):
                    updates["file_size"] = file_size
                    updates["download_link"] = download_link
                
                elif isinstance(product, ServiceProduct):
                    updates["duration"] = duration
                    updates["service_type"] = service_type
                
                inventory_manager.update_product(product_id, **updates)
                st.success(f"Product '{name}' updated successfully")
                
                del st.session_state.edit_product_id
                st.rerun()
            
            except Exception as e:
                st.error(f"Error updating product: {str(e)}")
        
        # Step 10.6: Handle cancel button
        if cancel_button:
            del st.session_state.edit_product_id
            st.rerun()
    
    except ProductNotFoundError:
        st.error(f"Product with ID {product_id} not found.")
        del st.session_state.edit_product_id
        st.rerun()


# Step 11: Define the main application function
def main():
    """Main application entry point.
    This sets up the app and controls the flow based on user authentication.
    """
    # Step 11.1: Configure the Streamlit app
    st.set_page_config(
        page_title="Inventory Management System",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Step 11.2: Add custom CSS for styling
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Step 11.3: Initialize authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Step 11.4: Show login page if not authenticated
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Step 11.5: Create an InventoryManager instance
    inventory_manager = InventoryManager()
    
    # Step 11.6: Show the sidebar and get the selected page
    page = sidebar_menu()
    
    # Step 11.7: Show the edit product page if editing
    if hasattr(st.session_state, 'edit_product_id'):
        edit_product_page(inventory_manager)
        return
    
    # Step 11.8: Show the selected page
    if page == "Dashboard":
        dashboard_page(inventory_manager)
    elif page == "Products":
        products_page(inventory_manager)
    elif page == "Add Product":
        add_product_page(inventory_manager)
    elif page == "Search":
        search_page(inventory_manager)
    elif page == "Stock Management":
        stock_management_page(inventory_manager)
    elif page == "Settings":
        settings_page(inventory_manager)


# Step 12: Run the application
if __name__ == "__main__":
    main()
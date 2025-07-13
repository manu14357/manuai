#!/usr/bin/env python3
"""
ArcOps Manufacturing Database Generator - 200 Tables Version
Part 1: Core Manufacturing Tables

This script generates a comprehensive manufacturing database with 200 tables
based on the ArcOps MES context. This is the first part focusing on core
manufacturing operations.
"""

import os
import sqlite3
from datetime import datetime


def create_database():
    """Create the main ArcOps manufacturing database with core tables"""
    
    # Database path
    db_path = "/Users/manu/Downloads/manuai/data/arcops_manufacturing_200.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    print("Creating ArcOps Manufacturing Database (200 tables) - Part 1...")
    
    # 1. CORE SYSTEM TABLES
    
    # System Configuration
    cursor.execute("""
    CREATE TABLE system_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_key TEXT NOT NULL UNIQUE,
        config_value TEXT,
        description TEXT,
        data_type TEXT DEFAULT 'string',
        is_encrypted BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # System Parameters
    cursor.execute("""
    CREATE TABLE system_parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parameter_name TEXT NOT NULL UNIQUE,
        parameter_value TEXT,
        parameter_type TEXT,
        category TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # System Logs
    cursor.execute("""
    CREATE TABLE system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_level TEXT NOT NULL,
        module TEXT,
        message TEXT,
        details TEXT,
        user_id INTEGER,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. ORGANIZATION STRUCTURE
    
    # Companies
    cursor.execute("""
    CREATE TABLE companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_code TEXT NOT NULL UNIQUE,
        company_name TEXT NOT NULL,
        legal_name TEXT,
        tax_id TEXT,
        address_line1 TEXT,
        address_line2 TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        country TEXT,
        phone TEXT,
        email TEXT,
        website TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Plants/Facilities
    cursor.execute("""
    CREATE TABLE plants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        plant_code TEXT NOT NULL UNIQUE,
        plant_name TEXT NOT NULL,
        plant_type TEXT,
        address_line1 TEXT,
        address_line2 TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        country TEXT,
        phone TEXT,
        email TEXT,
        manager_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id)
    )
    """)
    
    # Departments
    cursor.execute("""
    CREATE TABLE departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plant_id INTEGER NOT NULL,
        department_code TEXT NOT NULL,
        department_name TEXT NOT NULL,
        description TEXT,
        manager_id INTEGER,
        cost_center TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (plant_id) REFERENCES plants(id)
    )
    """)
    
    # Work Centers
    cursor.execute("""
    CREATE TABLE work_centers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department_id INTEGER NOT NULL,
        work_center_code TEXT NOT NULL UNIQUE,
        work_center_name TEXT NOT NULL,
        description TEXT,
        work_center_type TEXT,
        capacity_hours_per_day REAL,
        efficiency_factor REAL DEFAULT 1.0,
        cost_per_hour REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )
    """)
    
    # 3. PERSONNEL MANAGEMENT
    
    # Employees
    cursor.execute("""
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_number TEXT NOT NULL UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        hire_date DATE,
        termination_date DATE,
        job_title TEXT,
        department_id INTEGER,
        manager_id INTEGER,
        hourly_rate REAL,
        salary REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments(id),
        FOREIGN KEY (manager_id) REFERENCES employees(id)
    )
    """)
    
    # Skills
    cursor.execute("""
    CREATE TABLE skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_code TEXT NOT NULL UNIQUE,
        skill_name TEXT NOT NULL,
        description TEXT,
        skill_category TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Employee Skills
    cursor.execute("""
    CREATE TABLE employee_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        proficiency_level TEXT,
        certification_date DATE,
        expiration_date DATE,
        certified_by TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (skill_id) REFERENCES skills(id)
    )
    """)
    
    # Shifts
    cursor.execute("""
    CREATE TABLE shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shift_code TEXT NOT NULL UNIQUE,
        shift_name TEXT NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        break_duration INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 4. PRODUCTS AND ITEMS
    
    # Item Masters
    cursor.execute("""
    CREATE TABLE item_masters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_number TEXT NOT NULL UNIQUE,
        item_name TEXT NOT NULL,
        description TEXT,
        item_type TEXT,
        category TEXT,
        subcategory TEXT,
        unit_of_measure TEXT,
        weight REAL,
        length REAL,
        width REAL,
        height REAL,
        volume REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Products
    cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_code TEXT NOT NULL UNIQUE,
        product_name TEXT NOT NULL,
        description TEXT,
        product_family TEXT,
        product_line TEXT,
        version TEXT,
        status TEXT,
        launch_date DATE,
        discontinue_date DATE,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Bills of Materials (BOMs)
    cursor.execute("""
    CREATE TABLE boms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bom_number TEXT NOT NULL UNIQUE,
        product_id INTEGER NOT NULL,
        version TEXT,
        effective_date DATE,
        expiration_date DATE,
        status TEXT,
        notes TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    
    # BOM Items
    cursor.execute("""
    CREATE TABLE bom_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bom_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        sequence_number INTEGER,
        quantity REAL NOT NULL,
        unit_of_measure TEXT,
        scrap_factor REAL DEFAULT 0,
        is_optional BOOLEAN DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (bom_id) REFERENCES boms(id),
        FOREIGN KEY (item_id) REFERENCES item_masters(id)
    )
    """)
    
    # 5. ROUTINGS AND OPERATIONS
    
    # Routings
    cursor.execute("""
    CREATE TABLE routings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        routing_number TEXT NOT NULL UNIQUE,
        product_id INTEGER NOT NULL,
        version TEXT,
        effective_date DATE,
        expiration_date DATE,
        status TEXT,
        total_setup_time REAL,
        total_run_time REAL,
        notes TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    
    # Operations
    cursor.execute("""
    CREATE TABLE operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation_code TEXT NOT NULL UNIQUE,
        operation_name TEXT NOT NULL,
        description TEXT,
        operation_type TEXT,
        setup_time REAL,
        run_time_per_unit REAL,
        labor_hours_per_unit REAL,
        machine_hours_per_unit REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Routing Operations
    cursor.execute("""
    CREATE TABLE routing_operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        routing_id INTEGER NOT NULL,
        operation_id INTEGER NOT NULL,
        work_center_id INTEGER NOT NULL,
        sequence_number INTEGER NOT NULL,
        setup_time REAL,
        run_time_per_unit REAL,
        move_time REAL,
        queue_time REAL,
        overlap_quantity REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (routing_id) REFERENCES routings(id),
        FOREIGN KEY (operation_id) REFERENCES operations(id),
        FOREIGN KEY (work_center_id) REFERENCES work_centers(id)
    )
    """)
    
    # 6. CUSTOMER MANAGEMENT
    
    # Customers
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_code TEXT NOT NULL UNIQUE,
        customer_name TEXT NOT NULL,
        customer_type TEXT,
        industry TEXT,
        address_line1 TEXT,
        address_line2 TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        country TEXT,
        phone TEXT,
        email TEXT,
        website TEXT,
        credit_limit REAL,
        payment_terms TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Customer Contacts
    cursor.execute("""
    CREATE TABLE customer_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        title TEXT,
        phone TEXT,
        email TEXT,
        is_primary BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)
    
    # Sales Orders
    cursor.execute("""
    CREATE TABLE sales_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        customer_id INTEGER NOT NULL,
        order_date DATE NOT NULL,
        requested_date DATE,
        promised_date DATE,
        status TEXT,
        total_amount REAL,
        currency TEXT,
        notes TEXT,
        created_by INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)
    
    # Sales Order Items
    cursor.execute("""
    CREATE TABLE sales_order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sales_order_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        line_number INTEGER,
        quantity REAL NOT NULL,
        unit_price REAL,
        discount_percent REAL DEFAULT 0,
        line_total REAL,
        requested_date DATE,
        promised_date DATE,
        status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
        FOREIGN KEY (item_id) REFERENCES item_masters(id)
    )
    """)
    
    # 7. SUPPLIER MANAGEMENT
    
    # Suppliers
    cursor.execute("""
    CREATE TABLE suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_code TEXT NOT NULL UNIQUE,
        supplier_name TEXT NOT NULL,
        supplier_type TEXT,
        address_line1 TEXT,
        address_line2 TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        country TEXT,
        phone TEXT,
        email TEXT,
        website TEXT,
        payment_terms TEXT,
        quality_rating REAL,
        delivery_rating REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Supplier Contacts
    cursor.execute("""
    CREATE TABLE supplier_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        title TEXT,
        phone TEXT,
        email TEXT,
        is_primary BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
    """)
    
    # Purchase Orders
    cursor.execute("""
    CREATE TABLE purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_number TEXT NOT NULL UNIQUE,
        supplier_id INTEGER NOT NULL,
        order_date DATE NOT NULL,
        requested_date DATE,
        promised_date DATE,
        status TEXT,
        total_amount REAL,
        currency TEXT,
        notes TEXT,
        created_by INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
    """)
    
    # Purchase Order Items
    cursor.execute("""
    CREATE TABLE purchase_order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        purchase_order_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        line_number INTEGER,
        quantity REAL NOT NULL,
        unit_price REAL,
        line_total REAL,
        requested_date DATE,
        promised_date DATE,
        status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id),
        FOREIGN KEY (item_id) REFERENCES item_masters(id)
    )
    """)
    
    # 8. INVENTORY MANAGEMENT
    
    # Warehouses
    cursor.execute("""
    CREATE TABLE warehouses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        warehouse_code TEXT NOT NULL UNIQUE,
        warehouse_name TEXT NOT NULL,
        plant_id INTEGER NOT NULL,
        warehouse_type TEXT,
        address_line1 TEXT,
        address_line2 TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (plant_id) REFERENCES plants(id)
    )
    """)
    
    # Locations
    cursor.execute("""
    CREATE TABLE locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        warehouse_id INTEGER NOT NULL,
        location_code TEXT NOT NULL UNIQUE,
        location_name TEXT,
        location_type TEXT,
        aisle TEXT,
        bay TEXT,
        level TEXT,
        position TEXT,
        capacity REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
    )
    """)
    
    # Inventory
    cursor.execute("""
    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        lot_number TEXT,
        serial_number TEXT,
        quantity_on_hand REAL NOT NULL DEFAULT 0,
        quantity_allocated REAL DEFAULT 0,
        quantity_available REAL DEFAULT 0,
        unit_cost REAL,
        last_count_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES item_masters(id),
        FOREIGN KEY (location_id) REFERENCES locations(id)
    )
    """)
    
    # Inventory Transactions
    cursor.execute("""
    CREATE TABLE inventory_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        transaction_date DATE NOT NULL,
        quantity REAL NOT NULL,
        unit_cost REAL,
        total_cost REAL,
        lot_number TEXT,
        serial_number TEXT,
        reference_number TEXT,
        notes TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES item_masters(id),
        FOREIGN KEY (location_id) REFERENCES locations(id)
    )
    """)
    
    # 9. PRODUCTION PLANNING
    
    # Master Production Schedule
    cursor.execute("""
    CREATE TABLE master_production_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        period_start_date DATE NOT NULL,
        period_end_date DATE NOT NULL,
        planned_quantity REAL NOT NULL,
        actual_quantity REAL DEFAULT 0,
        status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    
    # Material Requirements Planning (MRP)
    cursor.execute("""
    CREATE TABLE mrp_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        requirement_date DATE NOT NULL,
        gross_requirement REAL NOT NULL,
        scheduled_receipts REAL DEFAULT 0,
        projected_available REAL DEFAULT 0,
        net_requirement REAL DEFAULT 0,
        planned_order_receipt REAL DEFAULT 0,
        planned_order_release REAL DEFAULT 0,
        source_type TEXT,
        source_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES item_masters(id)
    )
    """)
    
    # Production Plans
    cursor.execute("""
    CREATE TABLE production_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_number TEXT NOT NULL UNIQUE,
        product_id INTEGER NOT NULL,
        plan_date DATE NOT NULL,
        planned_quantity REAL NOT NULL,
        priority INTEGER,
        status TEXT,
        notes TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    
    # Commit the changes
    conn.commit()
    
    print(f"Database created successfully at: {db_path}")
    table_count = len(cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
    print(f"Created {table_count} tables so far...")
    
    return conn, cursor

if __name__ == "__main__":
    conn, cursor = create_database()
    conn.close()
    print("ArcOps Manufacturing Database (200 tables) - Part 1 completed!")

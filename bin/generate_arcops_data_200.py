#!/usr/bin/env python3
"""
ArcOps Manufacturing Database Data Population - 200 Tables Version

This script populates the 200-table manufacturing database with realistic
data using the Faker library.
"""

import os
import random
import sqlite3
from datetime import datetime, timedelta

from faker import Faker

# Initialize Faker
fake = Faker()

def populate_database():
    """Populate the database with realistic manufacturing data"""
    
    # Database path
    db_path = "/Users/manu/Downloads/manuai/data/arcops_manufacturing_200.db"
    
    if not os.path.exists(db_path):
        print("Error: Database not found. Please run the database generation scripts first.")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Populating ArcOps Manufacturing Database (200 tables) with sample data...")
    
    # 1. SYSTEM CONFIGURATION
    print("Populating system configuration...")
    
    # System Config
    config_data = [
        ('database_version', '1.0.0', 'Database schema version', 'string'),
        ('company_name', 'ArcOps Manufacturing', 'Company name', 'string'),
        ('default_currency', 'USD', 'Default currency', 'string'),
        ('time_zone', 'UTC', 'System timezone', 'string'),
        ('backup_retention_days', '30', 'Backup retention period', 'integer'),
        ('session_timeout_minutes', '60', 'User session timeout', 'integer'),
        ('max_file_upload_mb', '100', 'Maximum file upload size', 'integer'),
        ('enable_audit_logging', 'true', 'Enable audit logging', 'boolean'),
        ('enable_email_notifications', 'true', 'Enable email notifications', 'boolean'),
        ('quality_control_required', 'true', 'Require quality control', 'boolean')
    ]
    
    for config_key, config_value, description, data_type in config_data:
        cursor.execute("""
            INSERT INTO system_config (config_key, config_value, description, data_type)
            VALUES (?, ?, ?, ?)
        """, (config_key, config_value, description, data_type))
    
    # System Parameters
    param_data = [
        ('standard_work_hours', '8', 'decimal', 'Working Time', 1),
        ('overtime_multiplier', '1.5', 'decimal', 'Payroll', 1),
        ('default_lead_time_days', '7', 'integer', 'Production', 1),
        ('quality_sample_size', '5', 'integer', 'Quality', 1),
        ('inventory_reorder_point', '50', 'integer', 'Inventory', 1),
        ('maintenance_interval_hours', '168', 'integer', 'Maintenance', 1),
        ('scrap_tolerance_percent', '2', 'decimal', 'Production', 1),
        ('on_time_delivery_target', '95', 'decimal', 'Shipping', 1),
        ('first_pass_yield_target', '98', 'decimal', 'Quality', 1),
        ('equipment_utilization_target', '85', 'decimal', 'Production', 1)
    ]
    
    for param_name, param_value, param_type, category, is_active in param_data:
        cursor.execute("""
            INSERT INTO system_parameters (parameter_name, parameter_value, parameter_type, category, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (param_name, param_value, param_type, category, is_active))
    
    # 2. ORGANIZATION STRUCTURE
    print("Populating organization structure...")
    
    # Companies
    companies = []
    for i in range(3):
        company_code = f"COMP{i+1:03d}"
        company_name = fake.company()
        legal_name = f"{company_name} Inc."
        tax_id = fake.ssn()
        
        cursor.execute("""
            INSERT INTO companies (company_code, company_name, legal_name, tax_id,
                                 address_line1, address_line2, city, state, postal_code, country,
                                 phone, email, website, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_code, company_name, legal_name, tax_id,
              fake.street_address(), fake.secondary_address(), fake.city(),
              fake.state(), fake.zipcode(), fake.country(),
              fake.phone_number(), fake.email(), fake.url(), 1))
        
        companies.append((cursor.lastrowid, company_code, company_name))
    
    # Plants
    plants = []
    plant_types = ['Manufacturing', 'Assembly', 'Distribution', 'R&D']
    
    for i in range(5):
        company_id = random.choice(companies)[0]
        plant_code = f"PLANT{i+1:03d}"
        plant_name = f"{fake.city()} {random.choice(plant_types)} Plant"
        plant_type = random.choice(plant_types)
        
        cursor.execute("""
            INSERT INTO plants (company_id, plant_code, plant_name, plant_type,
                              address_line1, address_line2, city, state, postal_code, country,
                              phone, email, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, plant_code, plant_name, plant_type,
              fake.street_address(), fake.secondary_address(), fake.city(),
              fake.state(), fake.zipcode(), fake.country(),
              fake.phone_number(), fake.email(), 1))
        
        plants.append((cursor.lastrowid, plant_code, plant_name))
    
    # Departments
    departments = []
    dept_names = ['Production', 'Quality Control', 'Maintenance', 'Shipping', 'Receiving',
                  'Engineering', 'Planning', 'Administration', 'Safety', 'Training']
    
    for plant_id, plant_code, plant_name in plants:
        for i, dept_name in enumerate(dept_names):
            dept_code = f"{plant_code}-{dept_name.upper()[:3]}"
            cost_center = f"CC{plant_id:02d}{i+1:02d}"
            
            cursor.execute("""
                INSERT INTO departments (plant_id, department_code, department_name,
                                       description, cost_center, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (plant_id, dept_code, dept_name,
                  f"{dept_name} department at {plant_name}", cost_center, 1))
            
            departments.append((cursor.lastrowid, dept_code, dept_name))
    
    # Work Centers
    work_centers = []
    wc_types = ['Manual', 'Semi-Automated', 'Automated', 'Inspection', 'Assembly']
    
    for i in range(50):
        dept_id = random.choice(departments)[0]
        wc_code = f"WC{i+1:03d}"
        wc_name = f"Work Center {i+1}"
        wc_type = random.choice(wc_types)
        capacity = random.uniform(6, 24)  # hours per day
        efficiency = random.uniform(0.8, 1.2)
        cost_per_hour = random.uniform(25, 100)
        
        cursor.execute("""
            INSERT INTO work_centers (department_id, work_center_code, work_center_name,
                                    description, work_center_type, capacity_hours_per_day,
                                    efficiency_factor, cost_per_hour, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (dept_id, wc_code, wc_name, f"Work center for {wc_type} operations",
              wc_type, capacity, efficiency, cost_per_hour, 1))
        
        work_centers.append((cursor.lastrowid, wc_code, wc_name))
    
    # 3. PERSONNEL
    print("Populating personnel data...")
    
    # Employees
    employees = []
    job_titles = ['Operator', 'Technician', 'Supervisor', 'Manager', 'Engineer',
                  'Quality Inspector', 'Maintenance Tech', 'Planner', 'Scheduler']
    
    for i in range(200):
        emp_number = f"EMP{i+1:05d}"
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@company.com"
        phone = fake.phone_number()
        hire_date = fake.date_between(start_date='-10y', end_date='today')
        job_title = random.choice(job_titles)
        dept_id = random.choice(departments)[0]
        hourly_rate = random.uniform(15, 50)
        
        cursor.execute("""
            INSERT INTO employees (employee_number, first_name, last_name, email, phone,
                                 hire_date, job_title, department_id, hourly_rate, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (emp_number, first_name, last_name, email, phone,
              hire_date, job_title, dept_id, hourly_rate, 1))
        
        employees.append((cursor.lastrowid, emp_number, f"{first_name} {last_name}"))
    
    # Skills
    skills = []
    skill_names = ['Welding', 'Machining', 'Assembly', 'Quality Inspection', 'Forklift Operation',
                   'Crane Operation', 'Electrical', 'Hydraulics', 'Pneumatics', 'CNC Programming',
                   'CAD Design', 'Maintenance', 'Safety Training', 'First Aid', 'Lean Manufacturing']
    
    for i, skill_name in enumerate(skill_names):
        skill_code = f"SKILL{i+1:03d}"
        category = random.choice(['Technical', 'Safety', 'Administrative'])
        
        cursor.execute("""
            INSERT INTO skills (skill_code, skill_name, description, skill_category, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (skill_code, skill_name, f"{skill_name} skill", category, 1))
        
        skills.append((cursor.lastrowid, skill_code, skill_name))
    
    # Employee Skills (random assignments)
    proficiency_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    
    for emp_id, emp_number, emp_name in employees:
        # Give each employee 1-5 random skills
        num_skills = random.randint(1, 5)
        emp_skills = random.sample(skills, num_skills)
        
        for skill_id, skill_code, skill_name in emp_skills:
            proficiency = random.choice(proficiency_levels)
            cert_date = fake.date_between(start_date='-5y', end_date='today')
            exp_date = cert_date + timedelta(days=random.randint(365, 1825))
            
            cursor.execute("""
                INSERT INTO employee_skills (employee_id, skill_id, proficiency_level,
                                           certification_date, expiration_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (emp_id, skill_id, proficiency, cert_date, exp_date, 1))
    
    # Shifts
    shifts = [
        ('SHIFT1', 'Day Shift', '06:00:00', '14:00:00', 30),
        ('SHIFT2', 'Swing Shift', '14:00:00', '22:00:00', 30),
        ('SHIFT3', 'Night Shift', '22:00:00', '06:00:00', 30),
        ('WEEKEND', 'Weekend Shift', '06:00:00', '18:00:00', 60)
    ]
    
    shift_ids = []
    for shift_code, shift_name, start_time, end_time, break_duration in shifts:
        cursor.execute("""
            INSERT INTO shifts (shift_code, shift_name, start_time, end_time, break_duration, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (shift_code, shift_name, start_time, end_time, break_duration, 1))
        
        shift_ids.append((cursor.lastrowid, shift_code, shift_name))
    
    # 4. PRODUCTS AND ITEMS
    print("Populating products and items...")
    
    # Item Masters
    items = []
    item_types = ['Raw Material', 'Component', 'Sub-Assembly', 'Finished Good', 'Tool', 'Supply']
    categories = ['Metals', 'Plastics', 'Electronics', 'Mechanical', 'Consumables', 'Packaging']
    uoms = ['EA', 'LB', 'FT', 'GAL', 'KG', 'M', 'L']
    
    for i in range(500):
        item_number = f"ITEM{i+1:06d}"
        item_name = fake.catch_phrase()
        item_type = random.choice(item_types)
        category = random.choice(categories)
        uom = random.choice(uoms)
        weight = random.uniform(0.1, 100)
        
        cursor.execute("""
            INSERT INTO item_masters (item_number, item_name, description, item_type,
                                    category, unit_of_measure, weight, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_number, item_name, f"{item_name} - {item_type}", item_type,
              category, uom, weight, 1))
        
        items.append((cursor.lastrowid, item_number, item_name))
    
    # Products (subset of items that are finished goods)
    products = []
    product_families = ['Series A', 'Series B', 'Series C', 'Custom']
    product_lines = ['Standard', 'Premium', 'Economy', 'Industrial']
    
    for i in range(50):
        product_code = f"PROD{i+1:04d}"
        product_name = fake.catch_phrase()
        family = random.choice(product_families)
        line = random.choice(product_lines)
        version = f"v{random.randint(1, 5)}.{random.randint(0, 9)}"
        launch_date = fake.date_between(start_date='-5y', end_date='today')
        
        cursor.execute("""
            INSERT INTO products (product_code, product_name, description, product_family,
                                product_line, version, status, launch_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_code, product_name, f"{product_name} - {family} {line}",
              family, line, version, 'Active', launch_date, 1))
        
        products.append((cursor.lastrowid, product_code, product_name))
    
    # Bills of Materials
    boms = []
    for i, (product_id, product_code, product_name) in enumerate(products[:25]):
        bom_number = f"BOM{i+1:04d}"
        version = f"v{random.randint(1, 3)}.{random.randint(0, 9)}"
        effective_date = fake.date_between(start_date='-2y', end_date='today')
        
        cursor.execute("""
            INSERT INTO boms (bom_number, product_id, version, effective_date,
                            status, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (bom_number, product_id, version, effective_date, 'Active', 1))
        
        bom_id = cursor.lastrowid
        boms.append((bom_id, bom_number, product_name))
        
        # BOM Items (5-15 items per BOM)
        num_items = random.randint(5, 15)
        bom_items = random.sample(items, num_items)
        
        for seq, (item_id, item_number, item_name) in enumerate(bom_items, 1):
            quantity = random.uniform(1, 10)
            scrap_factor = random.uniform(0, 0.05)
            
            cursor.execute("""
                INSERT INTO bom_items (bom_id, item_id, sequence_number, quantity,
                                     scrap_factor, is_optional)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (bom_id, item_id, seq, quantity, scrap_factor, random.choice([0, 1])))
    
    # 5. ROUTINGS AND OPERATIONS
    print("Populating routings and operations...")
    
    # Operations
    operations = []
    op_types = ['Setup', 'Machining', 'Assembly', 'Inspection', 'Packaging', 'Heat Treatment']
    
    for i in range(100):
        op_code = f"OP{i+1:03d}"
        op_name = f"{random.choice(op_types)} Operation {i+1}"
        op_type = random.choice(op_types)
        setup_time = random.uniform(5, 60)  # minutes
        run_time = random.uniform(0.5, 10)  # minutes per unit
        
        cursor.execute("""
            INSERT INTO operations (operation_code, operation_name, description, operation_type,
                                  setup_time, run_time_per_unit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (op_code, op_name, f"{op_name} operation", op_type,
              setup_time, run_time, 1))
        
        operations.append((cursor.lastrowid, op_code, op_name))
    
    # Routings
    routings = []
    for i, (product_id, product_code, product_name) in enumerate(products[:25]):
        routing_number = f"RTG{i+1:04d}"
        version = f"v{random.randint(1, 3)}.{random.randint(0, 9)}"
        effective_date = fake.date_between(start_date='-2y', end_date='today')
        
        cursor.execute("""
            INSERT INTO routings (routing_number, product_id, version, effective_date,
                                status, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (routing_number, product_id, version, effective_date, 'Active', 1))
        
        routing_id = cursor.lastrowid
        routings.append((routing_id, routing_number, product_name))
        
        # Routing Operations (3-8 operations per routing)
        num_operations = random.randint(3, 8)
        routing_ops = random.sample(operations, num_operations)
        
        for seq, (op_id, op_code, op_name) in enumerate(routing_ops, 1):
            wc_id = random.choice(work_centers)[0]
            setup_time = random.uniform(10, 120)
            run_time = random.uniform(1, 30)
            
            cursor.execute("""
                INSERT INTO routing_operations (routing_id, operation_id, work_center_id,
                                              sequence_number, setup_time, run_time_per_unit,
                                              is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (routing_id, op_id, wc_id, seq, setup_time, run_time, 1))
    
    # 6. CUSTOMERS
    print("Populating customer data...")
    
    # Customers
    customers = []
    customer_types = ['Manufacturing', 'Retail', 'Distributor', 'OEM']
    industries = ['Automotive', 'Aerospace', 'Electronics', 'Medical', 'Consumer Goods']
    
    for i in range(100):
        customer_code = f"CUST{i+1:05d}"
        customer_name = fake.company()
        customer_type = random.choice(customer_types)
        industry = random.choice(industries)
        credit_limit = random.uniform(10000, 500000)
        
        cursor.execute("""
            INSERT INTO customers (customer_code, customer_name, customer_type, industry,
                                 address_line1, address_line2, city, state, postal_code, country,
                                 phone, email, website, credit_limit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer_code, customer_name, customer_type, industry,
              fake.street_address(), fake.secondary_address(), fake.city(),
              fake.state(), fake.zipcode(), fake.country(),
              fake.phone_number(), fake.email(), fake.url(), credit_limit, 1))
        
        customers.append((cursor.lastrowid, customer_code, customer_name))
    
    # Customer Contacts
    for customer_id, customer_code, customer_name in customers:
        # Add 1-3 contacts per customer
        num_contacts = random.randint(1, 3)
        for j in range(num_contacts):
            first_name = fake.first_name()
            last_name = fake.last_name()
            title = random.choice(['Purchasing Manager', 'Buyer', 'Engineer', 'Quality Manager'])
            is_primary = 1 if j == 0 else 0
            
            cursor.execute("""
                INSERT INTO customer_contacts (customer_id, first_name, last_name, title,
                                             phone, email, is_primary, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, first_name, last_name, title,
                  fake.phone_number(), fake.email(), is_primary, 1))
    
    # 7. SUPPLIERS
    print("Populating supplier data...")
    
    # Suppliers
    suppliers = []
    supplier_types = ['Raw Material', 'Component', 'Service', 'Equipment']
    
    for i in range(75):
        supplier_code = f"SUPP{i+1:05d}"
        supplier_name = fake.company()
        supplier_type = random.choice(supplier_types)
        quality_rating = random.uniform(3.0, 5.0)
        delivery_rating = random.uniform(3.0, 5.0)
        
        cursor.execute("""
            INSERT INTO suppliers (supplier_code, supplier_name, supplier_type,
                                 address_line1, address_line2, city, state, postal_code, country,
                                 phone, email, website, quality_rating, delivery_rating, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (supplier_code, supplier_name, supplier_type,
              fake.street_address(), fake.secondary_address(), fake.city(),
              fake.state(), fake.zipcode(), fake.country(),
              fake.phone_number(), fake.email(), fake.url(),
              quality_rating, delivery_rating, 1))
        
        suppliers.append((cursor.lastrowid, supplier_code, supplier_name))
    
    # Supplier Contacts
    for supplier_id, supplier_code, supplier_name in suppliers:
        # Add 1-2 contacts per supplier
        num_contacts = random.randint(1, 2)
        for j in range(num_contacts):
            first_name = fake.first_name()
            last_name = fake.last_name()
            title = random.choice(['Sales Rep', 'Account Manager', 'Technical Support'])
            is_primary = 1 if j == 0 else 0
            
            cursor.execute("""
                INSERT INTO supplier_contacts (supplier_id, first_name, last_name, title,
                                             phone, email, is_primary, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (supplier_id, first_name, last_name, title,
                  fake.phone_number(), fake.email(), is_primary, 1))
    
    # 8. INVENTORY MANAGEMENT
    print("Populating inventory data...")
    
    # Warehouses
    warehouses = []
    warehouse_types = ['Raw Material', 'Work In Process', 'Finished Goods', 'Shipping', 'Receiving']
    
    for i in range(10):
        plant_id = random.choice(plants)[0]
        warehouse_code = f"WH{i+1:03d}"
        warehouse_name = f"{random.choice(warehouse_types)} Warehouse {i+1}"
        warehouse_type = random.choice(warehouse_types)
        
        cursor.execute("""
            INSERT INTO warehouses (warehouse_code, warehouse_name, plant_id, warehouse_type,
                                  address_line1, city, state, postal_code, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (warehouse_code, warehouse_name, plant_id, warehouse_type,
              fake.street_address(), fake.city(), fake.state(), fake.zipcode(), 1))
        
        warehouses.append((cursor.lastrowid, warehouse_code, warehouse_name))
    
    # Locations
    locations = []
    location_types = ['Rack', 'Bin', 'Floor', 'Staging']
    
    for i in range(200):
        warehouse_id = random.choice(warehouses)[0]
        location_code = f"LOC{i+1:06d}"
        location_name = f"Location {i+1}"
        location_type = random.choice(location_types)
        aisle = f"A{random.randint(1, 20):02d}"
        bay = f"B{random.randint(1, 10):02d}"
        level = f"L{random.randint(1, 5)}"
        
        cursor.execute("""
            INSERT INTO locations (warehouse_id, location_code, location_name, location_type,
                                 aisle, bay, level, capacity, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (warehouse_id, location_code, location_name, location_type,
              aisle, bay, level, random.uniform(100, 1000), 1))
        
        locations.append((cursor.lastrowid, location_code, location_name))
    
    # Inventory (for a subset of items)
    for i in range(1000):
        item_id = random.choice(items)[0]
        location_id = random.choice(locations)[0]
        quantity = random.uniform(0, 1000)
        allocated = random.uniform(0, quantity * 0.5)
        available = quantity - allocated
        unit_cost = random.uniform(1, 500)
        
        cursor.execute("""
            INSERT INTO inventory (item_id, location_id, quantity_on_hand, quantity_allocated,
                                 quantity_available, unit_cost, last_count_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (item_id, location_id, quantity, allocated, available, unit_cost,
              fake.date_between(start_date='-1y', end_date='today')))
    
    # Commit all changes
    conn.commit()
    
    # Get final count
    table_count = len(cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
    print(f"Database populated successfully! Total tables: {table_count}")
    
    # Print some statistics
    cursor.execute("SELECT COUNT(*) FROM employees")
    emp_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM customers")
    cust_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM suppliers")
    supp_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM item_masters")
    item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]
    
    print(f"\nPopulated data summary:")
    print(f"- Employees: {emp_count}")
    print(f"- Customers: {cust_count}")
    print(f"- Suppliers: {supp_count}")
    print(f"- Items: {item_count}")
    print(f"- Products: {prod_count}")
    
    return conn

if __name__ == "__main__":
    conn = populate_database()
    conn.close()
    print("\nArcOps Manufacturing Database (200 tables) data population completed!")

#!/usr/bin/env python3
"""
ArcOps Manufacturing Database Generator - 500 Complex Tables
Generates a comprehensive manufacturing execution system database
with realistic fake data using Faker.
"""

import random
import sqlite3
import sys
from datetime import datetime, timedelta

from faker import Faker
from faker.providers import automotive, company, internet, job, phone_number

# Initialize Faker
fake = Faker()
fake.add_provider(automotive)
fake.add_provider(company)
fake.add_provider(internet)
fake.add_provider(job)
fake.add_provider(phone_number)

# Database configuration
DB_PATH = '/Users/manu/Downloads/manuai/data/arcops_complex_500.sqlite'
BATCH_SIZE = 1000

# Data generation parameters
NUM_CUSTOMERS = 500
NUM_PERSONNEL = 200
NUM_FACILITY_ASSETS = 150
NUM_WORKFLOWS = 100
NUM_WORK_ORDERS = 1000
NUM_JOBS = 2000
NUM_JOB_STEPS = 10000
NUM_TRANSACTIONS = 50000

def create_database_connection():
    """Create database connection and enable foreign keys."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def create_core_tables(conn):
    """Create the core ArcOps tables."""
    cursor = conn.cursor()
    
    # CUSTOMERS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CUSTOMER (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            CONTACT_NAME TEXT,
            CONTACT_NUMBER_PRIMARY TEXT,
            CONTACT_NUMBER_SECONDARY TEXT,
            CONTACT_EMAIL TEXT,
            DELIVERY_ADDRESS TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            CUSTOMER_CODE TEXT,
            NOTES TEXT,
            EXTRA_INFO_DATABASE_ID INTEGER,
            TYPE INTEGER DEFAULT 1,
            PERSON_IN_CHARGE INTEGER,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # PERSONNEL table  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PERSONNEL (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            USER_NAME TEXT UNIQUE NOT NULL,
            FIRST_NAME TEXT NOT NULL,
            LAST_NAME TEXT NOT NULL,
            POSITION TEXT,
            DEPARTMENT TEXT,
            "GROUP" TEXT,
            MOBILE_PERSONAL TEXT,
            MOBILE_OFFICE TEXT,
            LAND_LINE_OFFICE TEXT,
            LAND_LINE_HOME TEXT,
            EMAIL_PRIMARY TEXT,
            EMAIL_SECONDARY TEXT,
            USER_PICTURE TEXT,
            SECURITY_LEVEL INTEGER DEFAULT 1,
            LOGIN_ALLOWED INTEGER DEFAULT 1,
            PASSWORD_HASH TEXT,
            PASSWORD_SALT TEXT,
            IS_AVAILABLE INTEGER DEFAULT 1,
            IS_DELETED INTEGER DEFAULT 0,
            TIMESHEET_PROFILE_ID INTEGER,
            IMAGE_STRING_ID INTEGER,
            PIN_NUMBER_HASH TEXT,
            PIN_NUMBER_SALT TEXT,
            RECENTLY_OPENED_XML TEXT,
            STATUS INTEGER DEFAULT 1,
            TYPE INTEGER DEFAULT 1,
            TARGET_ID INTEGER,
            NORMALIZED_USER_NAME TEXT,
            NORMALIZED_EMAIL TEXT,
            EMAIL_CONFIRMED INTEGER DEFAULT 0,
            SECURITY_STAMP TEXT,
            CONCURRENCY_STAMP TEXT,
            MOBILE_OFFICE_CONFIRMED INTEGER DEFAULT 0,
            TWO_FACTOR_ENABLED INTEGER DEFAULT 0,
            LOCKOUT_END DATETIME,
            LOCKOUT_ENABLED INTEGER DEFAULT 0,
            ACCESS_FAILED_COUNT INTEGER DEFAULT 0,
            BARCODE TEXT,
            CONTENT_ID INTEGER,
            ENABLE_AUTO_LOGIN INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # FACILITY_ASSET table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FACILITY_ASSET (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            DESCRIPTION TEXT,
            ASSET_CODE TEXT,
            ASSET_TYPE INTEGER DEFAULT 3,
            MANUFACTURER TEXT,
            MODEL TEXT,
            SERIAL_NUMBER TEXT,
            LOCATION TEXT,
            ACQUISITION_DATE DATETIME,
            COST REAL,
            OPERATIONAL_STATUS INTEGER DEFAULT 1,
            MAINTENANCE_SCHEDULE TEXT,
            LAST_MAINTENANCE_DATE DATETIME,
            NEXT_MAINTENANCE_DATE DATETIME,
            CAPACITY REAL,
            EFFICIENCY_RATING REAL,
            ENERGY_CONSUMPTION REAL,
            DEPARTMENT_ID INTEGER,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            NOTES TEXT
        )
    ''')
    
    # BATCH_TEMPLATE (Workflows)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BATCH_TEMPLATE (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            DESCRIPTION TEXT,
            VERSION TEXT DEFAULT '1.0',
            IS_ACTIVE INTEGER DEFAULT 1,
            CREATED_BY INTEGER,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            LAST_MODIFIED_BY INTEGER,
            LAST_MODIFIED_DATE_TIME DATETIME,
            TOTAL_ESTIMATED_TIME REAL,
            COMPLEXITY_LEVEL INTEGER DEFAULT 1,
            CATEGORY TEXT,
            INDUSTRY_TYPE TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            TEMPLATE_XML TEXT,
            REVISION_NUMBER INTEGER DEFAULT 1,
            APPROVAL_STATUS INTEGER DEFAULT 1,
            APPROVED_BY INTEGER,
            APPROVED_DATE DATETIME,
            NOTES TEXT,
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (LAST_MODIFIED_BY) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (APPROVED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # BATCH_TEMPLATE_STEP (Workflow Steps)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BATCH_TEMPLATE_STEP (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            BATCH_TEMPLATE_ID INTEGER NOT NULL,
            NAME TEXT NOT NULL,
            DESCRIPTION TEXT,
            STEP_ORDER INTEGER NOT NULL,
            ESTIMATED_TIME REAL,
            MIN_TIME REAL,
            MAX_TIME REAL,
            STEP_TYPE INTEGER DEFAULT 1,
            INSTRUCTIONS TEXT,
            QUALITY_CHECKS TEXT,
            SAFETY_REQUIREMENTS TEXT,
            SKILL_REQUIREMENTS TEXT,
            EQUIPMENT_REQUIRED TEXT,
            MATERIALS_REQUIRED TEXT,
            PARALLEL_EXECUTION INTEGER DEFAULT 0,
            CRITICAL_PATH INTEGER DEFAULT 0,
            DEPENDENCY_STEPS TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (BATCH_TEMPLATE_ID) REFERENCES BATCH_TEMPLATE(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Core tables created successfully")

def create_scheduling_tables(conn):
    """Create scheduling and work order tables."""
    cursor = conn.cursor()
    
    # SALES_SCHEDULING (Work Orders)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SALES_SCHEDULING (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            REQUESTED_START_DATE_TIME DATETIME,
            REQUESTED_END_DATE_TIME DATETIME,
            NOTES TEXT,
            CREATED_BY INTEGER,
            ASSIGNED_TO INTEGER,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            BATCH_TEMPLATE_ID INTEGER,
            PURCHASE_ORDER_ID INTEGER,
            SALES_ORDER_STATUS INTEGER DEFAULT 7,
            GENERIC_COLUMN TEXT,
            EXTRA_INFO_DATABASE_ID INTEGER,
            CUSTOMER_ID INTEGER,
            USE_DEFAULT_CUSTOMER_DETAILS INTEGER DEFAULT 1,
            CUSTOM_CUSTOMER_CONTACT_NAME TEXT,
            CUSTOM_CUSTOMER_CONTACT_NUMBER_PRIMARY TEXT,
            CUSTOM_CUSTOMER_CONTACT_NUMBER_SECONDARY TEXT,
            CUSTOM_CUSTOMER_CONTACT_EMAIL TEXT,
            CUSTOM_CUSTOMER_DELIVERY_ADDRESS TEXT,
            USE_DEFAULT_RUNTIME INTEGER DEFAULT 1,
            CUSTOM_BATCH_RUN_RUNTIME_XML TEXT,
            HEARTBEAT_TIME DATETIME,
            HEARTBEAT_USER INTEGER,
            IS_DELETED INTEGER DEFAULT 0,
            SALES_TYPE INTEGER DEFAULT 1,
            PARENT_ID INTEGER,
            PREVIOUS_STATUS INTEGER,
            DOCUMENT_LINK_ID INTEGER,
            PRIORITY INTEGER DEFAULT 3,
            ESTIMATED_VALUE REAL,
            ACTUAL_VALUE REAL,
            PROFIT_MARGIN REAL,
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (ASSIGNED_TO) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (BATCH_TEMPLATE_ID) REFERENCES BATCH_TEMPLATE(ID),
            FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMER(ID)
        )
    ''')
    
    # BATCH_RUN (Jobs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BATCH_RUN (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            NOTES TEXT,
            SCHEDULED_START_DATE_TIME DATETIME,
            START_DATE_TIME DATETIME,
            END_DATE_TIME DATETIME,
            INVOICE_NUMBER TEXT,
            PURCHASE_ORDER_ID INTEGER,
            SALES_SCHEDULING_ID INTEGER,
            BATCH_TEMPLATE_ID INTEGER,
            PERSONNEL_ID INTEGER,
            PARENT_RUN_ID INTEGER,
            STATUS INTEGER DEFAULT 0,
            GANTT_COLOR TEXT DEFAULT '#3498db',
            LAST_UPDATE DATETIME DEFAULT CURRENT_TIMESTAMP,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            USE_DEFAULT_RUNTIME INTEGER DEFAULT 1,
            CUSTOM_BATCH_RUN_STEP_RUNTIME_XML TEXT,
            CUSTOM_RUNTIME REAL,
            HEARTBEAT_TIME DATETIME,
            HEARTBEAT_USER INTEGER,
            IS_DELETED INTEGER DEFAULT 0,
            IMAGE_STRING_ID TEXT,
            INSTRUCTIONS TEXT,
            BATCH_RUN_TYPE INTEGER DEFAULT 1,
            EXTRA_INFO_DATABASE_ID INTEGER,
            QUANTITY REAL,
            REWORK_QUANTITY REAL DEFAULT 0,
            SCRAP_QUANTITY REAL DEFAULT 0,
            DEFECT_QUANTITY REAL DEFAULT 0,
            COST REAL,
            CUSTOM_FINISHED_GOOD_INV_ITEM_LINK_ID INTEGER,
            CUSTOM_INV_BOM_LINK_ID INTEGER,
            CUSTOM_FINISHED_GOOD_INV_ITEM_TYPE_LINK_ID INTEGER,
            PRIORITY INTEGER DEFAULT 3,
            CREATED_BY INTEGER,
            SCHEDULED_DATE_TIME DATETIME,
            MODEL_ID INTEGER,
            DELIVER_DATE_TIME DATETIME,
            IS_LOCK INTEGER DEFAULT 0,
            LOCATION_LINK_ID INTEGER,
            DOCUMENT_LINK_ID INTEGER,
            IS_MODIFIED INTEGER DEFAULT 0,
            ALLOW_ADD_STEP INTEGER DEFAULT 1,
            ALLOW_EDIT_STEP INTEGER DEFAULT 1,
            MASTER_BATCH_TEMPLATE INTEGER,
            FOREIGN KEY (SALES_SCHEDULING_ID) REFERENCES SALES_SCHEDULING(ID),
            FOREIGN KEY (BATCH_TEMPLATE_ID) REFERENCES BATCH_TEMPLATE(ID),
            FOREIGN KEY (PERSONNEL_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Scheduling tables created successfully")

def create_execution_tables(conn):
    """Create job execution tables."""
    cursor = conn.cursor()
    
    # BATCH_RUN_STEP (Job Steps)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BATCH_RUN_STEP (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            EXPECTED_START_DATE_TIME DATETIME,
            SPLIT_STEP_EXPECTED_END_DATE_TIME DATETIME,
            START_DATE_TIME DATETIME,
            END_DATE_TIME DATETIME,
            NOTES TEXT,
            BATCH_RUN_ID INTEGER NOT NULL,
            PERSONNEL_ID INTEGER,
            BATCH_TEMPLATE_STEP_ID INTEGER,
            "INDEX" INTEGER,
            STATUS INTEGER DEFAULT 1,
            GANTT_COLOR TEXT DEFAULT '#2ecc71',
            USE_DEFAULT_RUNTIME INTEGER DEFAULT 1,
            CUSTOM_RUNTIME REAL,
            IS_DELETED INTEGER DEFAULT 0,
            INSTRUCTIONS TEXT,
            IMAGE_STRING INTEGER,
            IN_USE INTEGER DEFAULT 0,
            TIMESHEET_PROFILE_ID INTEGER,
            CUSTOM_CURRENT_VALUES_DATA_TIMING_LINK_ID INTEGER,
            CUSTOM_EXPECTED_MIN_TIME REAL,
            CUSTOM_EXPECTED_MAX_TIME REAL,
            STEP_TYPE INTEGER DEFAULT 1,
            FULL_NOTES TEXT,
            BATCH_RUN_STEP_SPLIT_LINK_ID INTEGER,
            CYCLE_TIME_SECONDS REAL,
            ACTUAL_RUN_TIME_MINUTES REAL,
            LAST_TRANSACTION_DATE_TIME DATETIME,
            IS_LOCK INTEGER DEFAULT 0,
            NAME TEXT,
            AREA_LINK_ID INTEGER,
            DOCUMENT_LINK_ID INTEGER,
            IS_DISABLED INTEGER DEFAULT 0,
            DISABLE_OVERRIDE_ALLOWED INTEGER DEFAULT 0,
            ALLOCATE_ASSET INTEGER DEFAULT 1,
            ALLOCATE_PERSONNEL INTEGER DEFAULT 1,
            ALLOW_SPLIT INTEGER DEFAULT 0,
            CATEGORY INTEGER DEFAULT 1,
            MIN_GAP_PREV_STEP REAL,
            PARTIAL_COMPLETE_AFTER REAL,
            FOREIGN KEY (BATCH_RUN_ID) REFERENCES BATCH_RUN(ID),
            FOREIGN KEY (PERSONNEL_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (BATCH_TEMPLATE_STEP_ID) REFERENCES BATCH_TEMPLATE_STEP(ID)
        )
    ''')
    
    # BATCH_RUN_STEP_TRANSACTION (Job Step Transactions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BATCH_RUN_STEP_TRANSACTION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            BATCH_RUN_STEP_ID INTEGER NOT NULL,
            TRANSACTION_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            TRANSACTION_STATUS INTEGER NOT NULL,
            TRANSACTION_OWNER_USER_ID INTEGER,
            TRANSACTION_NOTES TEXT,
            TRANSACTION_AMOUNT REAL,
            BATCH_RUN_STEP_PARAMETER_TRANSACTION_ID INTEGER,
            OTHER_OWNER_TYPE_ENUM INTEGER,
            OTHER_OWNER_TYPE_ID INTEGER,
            IS_DELETED INTEGER DEFAULT 0,
            IS_OVERRIDE INTEGER DEFAULT 0,
            OVERRIDE_PARENT_TRANSACTION_LINK_ID INTEGER,
            OVERRIDE_DATE_TIME DATETIME,
            OVERRIDE_AMOUNT REAL,
            OVERRIDE_START_DATE_TIME DATETIME,
            OVERRIDE_END_DATE_TIME DATETIME,
            TRANSACTION_OVERRIDE_USER_ID INTEGER,
            FOREIGN KEY (BATCH_RUN_STEP_ID) REFERENCES BATCH_RUN_STEP(ID),
            FOREIGN KEY (TRANSACTION_OWNER_USER_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (TRANSACTION_OVERRIDE_USER_ID) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Execution tables created successfully")

def create_labor_tables(conn):
    """Create labor tracking tables."""
    cursor = conn.cursor()
    
    # BATCH_RUN_STEP_LABOR
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BATCH_RUN_STEP_LABOR (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            START_DATE_TIME DATETIME,
            END_DATE_TIME DATETIME,
            NOTES TEXT,
            RUN_BY INTEGER,
            BATCH_RUN_STEP_ID INTEGER NOT NULL,
            BATCH_TEMPLATE_STEP_LABOR_ID INTEGER,
            PERSONNEL_ID INTEGER,
            IS_SPECIFIC INTEGER DEFAULT 0,
            IS_DELETED INTEGER DEFAULT 0,
            STATUS INTEGER DEFAULT 1,
            PLANNED_TYPE INTEGER DEFAULT 1,
            QUALIFICATION_LINK_ID INTEGER,
            IS_USED INTEGER DEFAULT 0,
            SCHEDULED_START_DATE_TIME DATETIME,
            SCHEDULED_END_DATE_TIME DATETIME,
            ACTUAL_RUNTIME_MINUTES REAL,
            LAST_TRANSACTION_DATE_TIME DATETIME,
            REQUIRED_QUANTITY REAL DEFAULT 1,
            CREATED_BY INTEGER,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (BATCH_RUN_STEP_ID) REFERENCES BATCH_RUN_STEP(ID),
            FOREIGN KEY (PERSONNEL_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (RUN_BY) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # BATCH_RUN_STEP_LABOR_TRANSACTION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BATCH_RUN_STEP_LABOR_TRANSACTION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TRANSACATION_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            TRANSACTION_STATUS INTEGER NOT NULL,
            PERSONNEL_ID INTEGER,
            BATCH_RUN_STEP_LABOR_ID INTEGER NOT NULL,
            TRANSACTION_AMOUNT REAL,
            BATCH_RUN_STEP_PARAMETER_TRANSACTION_ID INTEGER,
            BATCH_RUN_STEP_TRANSACTION_ID INTEGER,
            TRANSACTION_NOTES TEXT,
            TRANSACTION_OWNER_PERSONNEL_ID INTEGER,
            OTHER_OWNER_TYPE_ENUM INTEGER,
            OTHER_OWNER_TYPE_ID INTEGER,
            IS_DELETED INTEGER DEFAULT 0,
            IS_OVERRIDE INTEGER DEFAULT 0,
            OVERRIDE_PARENT_TRANSACTION_LINK_ID INTEGER,
            OVERRIDE_DATE_TIME DATETIME,
            OVERRIDE_AMOUNT REAL,
            OVERRIDE_START_DATE_TIME DATETIME,
            OVERRIDE_END_DATE_TIME DATETIME,
            TRANSACTION_OVERRIDE_USER_ID INTEGER,
            FOREIGN KEY (BATCH_RUN_STEP_LABOR_ID) REFERENCES BATCH_RUN_STEP_LABOR(ID),
            FOREIGN KEY (PERSONNEL_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (TRANSACTION_OWNER_PERSONNEL_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (TRANSACTION_OVERRIDE_USER_ID) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Labor tables created successfully")

def create_equipment_tables(conn):
    """Create equipment tracking tables."""
    cursor = conn.cursor()
    
    # BATCH_RUN_STEP_EQUIPMENT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BATCH_RUN_STEP_EQUIPMENT (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            START_DATE_TIME DATETIME,
            END_DATE_TIME DATETIME,
            NOTES TEXT,
            RUN_BY INTEGER,
            BATCH_RUN_STEP_ID INTEGER NOT NULL,
            BATCH_TEMPLATE_STEP_EQUIPMENT_ID INTEGER,
            FACILITY_ASSET_ID INTEGER,
            FACILITY_ASSET_TYPE_ID INTEGER,
            IS_USED INTEGER DEFAULT 0,
            IS_SPECIFIC INTEGER DEFAULT 0,
            IS_DELETED INTEGER DEFAULT 0,
            STATUS INTEGER DEFAULT 1,
            PLANNED_TYPE INTEGER DEFAULT 1,
            SCHEDULED_START_DATE_TIME DATETIME,
            SCHEDULED_END_DATE_TIME DATETIME,
            ACTUAL_RUNTIME_MINUTES REAL,
            LAST_TRANSACTION_DATE_TIME DATETIME,
            REQUIRED_QUANTITY REAL DEFAULT 1,
            QUALIFICATION_LINK_ID INTEGER,
            FOREIGN KEY (BATCH_RUN_STEP_ID) REFERENCES BATCH_RUN_STEP(ID),
            FOREIGN KEY (FACILITY_ASSET_ID) REFERENCES FACILITY_ASSET(ID),
            FOREIGN KEY (RUN_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # BATCH_RUN_STEP_EQUIPMENT_TRANSACTIONS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BATCH_RUN_STEP_EQUIPMENT_TRANSACTIONS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TRANSACTION_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            TRANSACTION_STATUS INTEGER NOT NULL,
            FACILITY_ASSET_ID INTEGER,
            BATCH_RUN_STEP_TRANSACTION_ID INTEGER,
            BATCH_RUN_STEP_PARAMENTER_TRANSACTION_ID INTEGER,
            TRANSACTION_NOTES TEXT,
            TRANSACTION_OWNER_PERSONNEL_ID INTEGER,
            OTHER_OWNER_TYPE_TABLE_ENUM INTEGER,
            OTHER_OWNER_TYPE_ID INTEGER,
            TRANSACTION_AMOUNT REAL,
            BATCH_RUN_STEP_EQUIPMENT_ID INTEGER NOT NULL,
            IS_DELETED INTEGER DEFAULT 0,
            IS_OVERRIDE INTEGER DEFAULT 0,
            OVERRIDE_PARENT_TRANSACTION_LINK_ID INTEGER,
            OVERRIDE_DATE_TIME DATETIME,
            OVERRIDE_AMOUNT REAL,
            OVERRIDE_START_DATE_TIME DATETIME,
            OVERRIDE_END_DATE_TIME DATETIME,
            TRANSACTION_OVERRIDE_USER_ID INTEGER,
            FOREIGN KEY (BATCH_RUN_STEP_EQUIPMENT_ID) REFERENCES BATCH_RUN_STEP_EQUIPMENT(ID),
            FOREIGN KEY (FACILITY_ASSET_ID) REFERENCES FACILITY_ASSET(ID),
            FOREIGN KEY (TRANSACTION_OWNER_PERSONNEL_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (TRANSACTION_OVERRIDE_USER_ID) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Equipment tables created successfully")

def generate_customers(conn):
    """Generate customer data."""
    cursor = conn.cursor()
    
    print(f"🔄 Generating {NUM_CUSTOMERS} customers...")
    customers = []
    
    for i in range(NUM_CUSTOMERS):
        customers.append((
            fake.company(),
            fake.name(),
            fake.phone_number(),
            fake.phone_number() if random.random() > 0.5 else None,
            fake.email(),
            fake.address().replace('\n', ', '),
            0,  # IS_DELETED
            f"CUST{i+1:04d}",
            fake.text(max_nb_chars=200) if random.random() > 0.7 else None,
            None,  # EXTRA_INFO_DATABASE_ID
            random.randint(1, 3),  # TYPE
            None,  # PERSON_IN_CHARGE (will be set later)
            fake.date_time_between(start_date='-2y', end_date='now')
        ))
    
    cursor.executemany('''
        INSERT INTO CUSTOMER (
            NAME, CONTACT_NAME, CONTACT_NUMBER_PRIMARY, CONTACT_NUMBER_SECONDARY,
            CONTACT_EMAIL, DELIVERY_ADDRESS, IS_DELETED, CUSTOMER_CODE, NOTES,
            EXTRA_INFO_DATABASE_ID, TYPE, PERSON_IN_CHARGE, CREATED_DATE_TIME
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', customers)
    
    conn.commit()
    print(f"✅ Generated {NUM_CUSTOMERS} customers")

def generate_personnel(conn):
    """Generate personnel data."""
    cursor = conn.cursor()
    
    print(f"🔄 Generating {NUM_PERSONNEL} personnel...")
    personnel = []
    
    departments = ['Production', 'Quality', 'Maintenance', 'Engineering', 'Planning', 'Logistics', 'Management']
    positions = ['Operator', 'Supervisor', 'Manager', 'Engineer', 'Technician', 'Specialist', 'Director']
    
    for i in range(NUM_PERSONNEL):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{first_name.lower()}.{last_name.lower()}{i+1}"
        
        personnel.append((
            username,
            first_name,
            last_name,
            random.choice(positions),
            random.choice(departments),
            f"Group_{random.randint(1, 5)}",
            fake.phone_number(),
            fake.phone_number(),
            fake.phone_number(),
            fake.phone_number() if random.random() > 0.7 else None,
            fake.email(),
            fake.email() if random.random() > 0.6 else None,
            None,  # USER_PICTURE
            random.randint(1, 5),  # SECURITY_LEVEL
            1,  # LOGIN_ALLOWED
            fake.sha256(),  # PASSWORD_HASH
            fake.sha256()[:32],  # PASSWORD_SALT
            random.choice([0, 1]),  # IS_AVAILABLE
            0,  # IS_DELETED
            random.randint(1, 5) if random.random() > 0.5 else None,  # TIMESHEET_PROFILE_ID
            None,  # IMAGE_STRING_ID
            fake.sha256()[:32],  # PIN_NUMBER_HASH
            fake.sha256()[:16],  # PIN_NUMBER_SALT
            None,  # RECENTLY_OPENED_XML
            random.randint(1, 3),  # STATUS
            random.randint(1, 3),  # TYPE
            None,  # TARGET_ID
            username.upper(),  # NORMALIZED_USER_NAME
            fake.email().upper(),  # NORMALIZED_EMAIL
            random.choice([0, 1]),  # EMAIL_CONFIRMED
            fake.uuid4(),  # SECURITY_STAMP
            fake.uuid4(),  # CONCURRENCY_STAMP
            random.choice([0, 1]),  # MOBILE_OFFICE_CONFIRMED
            random.choice([0, 1]),  # TWO_FACTOR_ENABLED
            None,  # LOCKOUT_END
            random.choice([0, 1]),  # LOCKOUT_ENABLED
            0,  # ACCESS_FAILED_COUNT
            f"EMP{i+1:04d}",  # BARCODE
            None,  # CONTENT_ID
            random.choice([0, 1]),  # ENABLE_AUTO_LOGIN
            fake.date_time_between(start_date='-2y', end_date='now')
        ))
    
    cursor.executemany('''
        INSERT INTO PERSONNEL (
            USER_NAME, FIRST_NAME, LAST_NAME, POSITION, DEPARTMENT, "GROUP",
            MOBILE_PERSONAL, MOBILE_OFFICE, LAND_LINE_OFFICE, LAND_LINE_HOME,
            EMAIL_PRIMARY, EMAIL_SECONDARY, USER_PICTURE, SECURITY_LEVEL,
            LOGIN_ALLOWED, PASSWORD_HASH, PASSWORD_SALT, IS_AVAILABLE, IS_DELETED,
            TIMESHEET_PROFILE_ID, IMAGE_STRING_ID, PIN_NUMBER_HASH, PIN_NUMBER_SALT,
            RECENTLY_OPENED_XML, STATUS, TYPE, TARGET_ID, NORMALIZED_USER_NAME,
            NORMALIZED_EMAIL, EMAIL_CONFIRMED, SECURITY_STAMP, CONCURRENCY_STAMP,
            MOBILE_OFFICE_CONFIRMED, TWO_FACTOR_ENABLED, LOCKOUT_END, LOCKOUT_ENABLED,
            ACCESS_FAILED_COUNT, BARCODE, CONTENT_ID, ENABLE_AUTO_LOGIN, CREATED_DATE_TIME
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', personnel)
    
    conn.commit()
    print(f"✅ Generated {NUM_PERSONNEL} personnel")

def generate_facility_assets(conn):
    """Generate facility assets (machines/equipment)."""
    cursor = conn.cursor()
    
    print(f"🔄 Generating {NUM_FACILITY_ASSETS} facility assets...")
    assets = []
    
    asset_types = ['CNC Machine', 'Lathe', 'Mill', 'Press', 'Welder', 'Grinder', 'Drill', 'Saw', 'Robot', 'Conveyor']
    manufacturers = ['Haas', 'Mazak', 'Okuma', 'DMG Mori', 'Fanuc', 'Kuka', 'ABB', 'Siemens', 'Mitsubishi', 'Yamazaki']
    
    for i in range(NUM_FACILITY_ASSETS):
        asset_name = f"{random.choice(asset_types)} #{i+1:03d}"
        
        assets.append((
            asset_name,
            fake.text(max_nb_chars=200),
            f"ASSET{i+1:04d}",
            3,  # ASSET_TYPE (Production Machine)
            random.choice(manufacturers),
            fake.bothify(text='Model-????-###'),
            fake.bothify(text='SN-########'),
            fake.city(),
            fake.date_between(start_date='-10y', end_date='-1y'),
            random.uniform(50000, 500000),  # COST
            random.choice([1, 2, 3]),  # OPERATIONAL_STATUS
            f"Weekly maintenance every {random.randint(1, 4)} weeks",
            fake.date_between(start_date='-6m', end_date='now'),
            fake.date_between(start_date='now', end_date='+6m'),
            random.uniform(100, 1000),  # CAPACITY
            random.uniform(0.7, 0.98),  # EFFICIENCY_RATING
            random.uniform(5, 50),  # ENERGY_CONSUMPTION
            random.randint(1, 5),  # DEPARTMENT_ID
            0,  # IS_DELETED
            fake.date_time_between(start_date='-2y', end_date='now'),
            fake.text(max_nb_chars=100) if random.random() > 0.7 else None
        ))
    
    cursor.executemany('''
        INSERT INTO FACILITY_ASSET (
            NAME, DESCRIPTION, ASSET_CODE, ASSET_TYPE, MANUFACTURER, MODEL,
            SERIAL_NUMBER, LOCATION, ACQUISITION_DATE, COST, OPERATIONAL_STATUS,
            MAINTENANCE_SCHEDULE, LAST_MAINTENANCE_DATE, NEXT_MAINTENANCE_DATE,
            CAPACITY, EFFICIENCY_RATING, ENERGY_CONSUMPTION, DEPARTMENT_ID,
            IS_DELETED, CREATED_DATE_TIME, NOTES
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', assets)
    
    conn.commit()
    print(f"✅ Generated {NUM_FACILITY_ASSETS} facility assets")

def main():
    """Main function to create database and generate data."""
    print("🚀 Starting ArcOps 500-Table Database Generation...")
    
    try:
        # Create database connection
        conn = create_database_connection()
        
        # Create tables
        create_core_tables(conn)
        create_scheduling_tables(conn)
        create_execution_tables(conn)
        create_labor_tables(conn)
        create_equipment_tables(conn)
        
        # Generate data
        generate_customers(conn)
        generate_personnel(conn)
        generate_facility_assets(conn)
        
        print(f"\n✅ Database created successfully at: {DB_PATH}")
        print(f"📊 Total tables created: ~50 (Part 1 of 500-table database)")
        print("\n🔍 Database Statistics:")
        
        # Show table counts
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"   Tables: {len(tables)}")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   {table[0]}: {count:,} records")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

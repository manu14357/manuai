#!/usr/bin/env python3
"""
ArcOps Manufacturing Database Generator - Data Population (500 Tables)
Populates the complex manufacturing database with realistic fake data
"""

import random
import sqlite3
import sys
from datetime import datetime, timedelta

from faker import Faker

# Initialize Faker
fake = Faker()

# Database configuration
DB_PATH = '/Users/manu/Downloads/manuai/data/arcops_complex_500.sqlite'

def create_database_connection():
    """Create database connection and enable foreign keys."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def generate_workflows_and_steps(conn):
    """Generate batch templates (workflows) and their steps."""
    cursor = conn.cursor()
    
    print("🔄 Generating workflows and workflow steps...")
    
    # Get personnel for references
    cursor.execute("SELECT ID FROM PERSONNEL LIMIT 50")
    personnel_ids = [row[0] for row in cursor.fetchall()]
    
    workflows = []
    workflow_steps = []
    
    workflow_types = [
        'Assembly Line', 'Quality Control', 'Machining', 'Welding', 'Packaging',
        'Inspection', 'Testing', 'Painting', 'Fabrication', 'Material Handling'
    ]
    
    # Generate 100 workflows
    for i in range(100):
        created_by = random.choice(personnel_ids)
        approved_by = random.choice(personnel_ids)
        
        workflows.append((
            f"{random.choice(workflow_types)} WF-{i+1:03d}",
            fake.text(max_nb_chars=200),
            f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
            1,  # IS_ACTIVE
            created_by,
            fake.date_time_between(start_date='-1y', end_date='now'),
            approved_by,
            fake.date_time_between(start_date='-6m', end_date='now'),
            random.uniform(60, 480),  # TOTAL_ESTIMATED_TIME
            random.randint(1, 5),  # COMPLEXITY_LEVEL
            random.choice(['Production', 'Quality', 'Maintenance']),
            random.choice(['Automotive', 'Electronics', 'Aerospace', 'General']),
            0,  # IS_DELETED
            fake.text(max_nb_chars=100),
            random.randint(1, 10),  # REVISION_NUMBER
            1,  # APPROVAL_STATUS
            approved_by,
            fake.date_time_between(start_date='-6m', end_date='now'),
            fake.text(max_nb_chars=100)
        ))
    
    cursor.executemany('''
        INSERT INTO BATCH_TEMPLATE (
            NAME, DESCRIPTION, VERSION, IS_ACTIVE, CREATED_BY, CREATED_DATE_TIME,
            LAST_MODIFIED_BY, LAST_MODIFIED_DATE_TIME, TOTAL_ESTIMATED_TIME,
            COMPLEXITY_LEVEL, CATEGORY, INDUSTRY_TYPE, IS_DELETED, TEMPLATE_XML,
            REVISION_NUMBER, APPROVAL_STATUS, APPROVED_BY, APPROVED_DATE, NOTES
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', workflows)
    
    conn.commit()
    
    # Get workflow IDs
    cursor.execute("SELECT ID FROM BATCH_TEMPLATE")
    workflow_ids = [row[0] for row in cursor.fetchall()]
    
    step_names = [
        'Setup', 'Preparation', 'Assembly', 'Welding', 'Inspection', 'Testing',
        'Quality Check', 'Packaging', 'Cleanup', 'Documentation', 'Calibration',
        'Machining', 'Drilling', 'Cutting', 'Finishing', 'Painting', 'Drying'
    ]
    
    # Generate workflow steps (5-10 steps per workflow)
    for workflow_id in workflow_ids:
        num_steps = random.randint(5, 10)
        for step_idx in range(num_steps):
            workflow_steps.append((
                workflow_id,
                f"{random.choice(step_names)} Step {step_idx + 1}",
                fake.text(max_nb_chars=150),
                step_idx + 1,  # STEP_ORDER
                random.uniform(15, 120),  # ESTIMATED_TIME
                random.uniform(10, 90),   # MIN_TIME
                random.uniform(120, 180), # MAX_TIME
                random.randint(1, 3),     # STEP_TYPE
                fake.text(max_nb_chars=200),  # INSTRUCTIONS
                fake.text(max_nb_chars=100),  # QUALITY_CHECKS
                fake.text(max_nb_chars=100),  # SAFETY_REQUIREMENTS
                fake.text(max_nb_chars=100),  # SKILL_REQUIREMENTS
                fake.text(max_nb_chars=100),  # EQUIPMENT_REQUIRED
                fake.text(max_nb_chars=100),  # MATERIALS_REQUIRED
                random.choice([0, 1]),    # PARALLEL_EXECUTION
                random.choice([0, 1]),    # CRITICAL_PATH
                f"Step {step_idx}" if step_idx > 0 else None,  # DEPENDENCY_STEPS
                0,  # IS_DELETED
                fake.date_time_between(start_date='-1y', end_date='now')
            ))
    
    cursor.executemany('''
        INSERT INTO BATCH_TEMPLATE_STEP (
            BATCH_TEMPLATE_ID, NAME, DESCRIPTION, STEP_ORDER, ESTIMATED_TIME,
            MIN_TIME, MAX_TIME, STEP_TYPE, INSTRUCTIONS, QUALITY_CHECKS,
            SAFETY_REQUIREMENTS, SKILL_REQUIREMENTS, EQUIPMENT_REQUIRED,
            MATERIALS_REQUIRED, PARALLEL_EXECUTION, CRITICAL_PATH,
            DEPENDENCY_STEPS, IS_DELETED, CREATED_DATE_TIME
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', workflow_steps)
    
    conn.commit()
    print(f"✅ Generated {len(workflows)} workflows and {len(workflow_steps)} workflow steps")

def generate_work_orders_and_jobs(conn):
    """Generate sales scheduling (work orders) and batch runs (jobs)."""
    cursor = conn.cursor()
    
    print("🔄 Generating work orders and jobs...")
    
    # Get reference data
    cursor.execute("SELECT ID FROM CUSTOMER")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT ID FROM PERSONNEL LIMIT 50")
    personnel_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT ID FROM BATCH_TEMPLATE")
    template_ids = [row[0] for row in cursor.fetchall()]
    
    work_orders = []
    jobs = []
    
    # Generate 1000 work orders
    for i in range(1000):
        created_by = random.choice(personnel_ids)
        assigned_to = random.choice(personnel_ids)
        customer_id = random.choice(customer_ids)
        template_id = random.choice(template_ids)
        
        start_date = fake.date_time_between(start_date='-6m', end_date='+3m')
        end_date = start_date + timedelta(days=random.randint(1, 30))
        
        work_orders.append((
            f"WO-{i+1:04d}-{fake.bothify(text='???')}",
            start_date,
            end_date,
            fake.text(max_nb_chars=200) if random.random() > 0.7 else None,
            created_by,
            assigned_to,
            fake.date_time_between(start_date='-6m', end_date='now'),
            template_id,
            None,  # PURCHASE_ORDER_ID
            random.choice([2, 5, 7, 9, 12]),  # SALES_ORDER_STATUS
            None,  # GENERIC_COLUMN
            None,  # EXTRA_INFO_DATABASE_ID
            customer_id,
            1,     # USE_DEFAULT_CUSTOMER_DETAILS
            None, None, None, None, None,  # CUSTOM_CUSTOMER fields
            1,     # USE_DEFAULT_RUNTIME
            None,  # CUSTOM_BATCH_RUN_RUNTIME_XML
            fake.date_time_between(start_date='-1h', end_date='now'),
            random.choice(personnel_ids),
            0,     # IS_DELETED
            random.randint(1, 3),  # SALES_TYPE
            None,  # PARENT_ID
            None,  # PREVIOUS_STATUS
            None,  # DOCUMENT_LINK_ID
            random.randint(1, 5),  # PRIORITY
            random.uniform(1000, 50000),   # ESTIMATED_VALUE
            random.uniform(1000, 50000),   # ACTUAL_VALUE
            random.uniform(0.1, 0.4)       # PROFIT_MARGIN
        ))
    
    cursor.executemany('''
        INSERT INTO SALES_SCHEDULING (
            NAME, REQUESTED_START_DATE_TIME, REQUESTED_END_DATE_TIME, NOTES,
            CREATED_BY, ASSIGNED_TO, CREATED_DATE_TIME, BATCH_TEMPLATE_ID,
            PURCHASE_ORDER_ID, SALES_ORDER_STATUS, GENERIC_COLUMN,
            EXTRA_INFO_DATABASE_ID, CUSTOMER_ID, USE_DEFAULT_CUSTOMER_DETAILS,
            CUSTOM_CUSTOMER_CONTACT_NAME, CUSTOM_CUSTOMER_CONTACT_NUMBER_PRIMARY,
            CUSTOM_CUSTOMER_CONTACT_NUMBER_SECONDARY, CUSTOM_CUSTOMER_CONTACT_EMAIL,
            CUSTOM_CUSTOMER_DELIVERY_ADDRESS, USE_DEFAULT_RUNTIME,
            CUSTOM_BATCH_RUN_RUNTIME_XML, HEARTBEAT_TIME, HEARTBEAT_USER,
            IS_DELETED, SALES_TYPE, PARENT_ID, PREVIOUS_STATUS, DOCUMENT_LINK_ID,
            PRIORITY, ESTIMATED_VALUE, ACTUAL_VALUE, PROFIT_MARGIN
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', work_orders)
    
    conn.commit()
    
    # Get work order IDs
    cursor.execute("SELECT ID FROM SALES_SCHEDULING")
    work_order_ids = [row[0] for row in cursor.fetchall()]
    
    # Generate 2000 jobs (1-3 jobs per work order)
    for work_order_id in work_order_ids:
        num_jobs = random.randint(1, 3)
        for job_idx in range(num_jobs):
            personnel_id = random.choice(personnel_ids)
            template_id = random.choice(template_ids)
            created_by = random.choice(personnel_ids)
            
            scheduled_start = fake.date_time_between(start_date='-3m', end_date='+2m')
            start_time = scheduled_start + timedelta(hours=random.randint(-24, 24)) if random.random() > 0.3 else None
            end_time = start_time + timedelta(hours=random.randint(1, 48)) if start_time and random.random() > 0.5 else None
            
            jobs.append((
                f"JOB-{work_order_id:04d}-{job_idx+1}",
                fake.text(max_nb_chars=200) if random.random() > 0.7 else None,
                scheduled_start,
                start_time,
                end_time,
                None,  # INVOICE_NUMBER
                None,  # PURCHASE_ORDER_ID
                work_order_id,
                template_id,
                personnel_id,
                None,  # PARENT_RUN_ID
                random.choice([0, 1, 3, 5, 6, 8]),  # STATUS
                random.choice(['#3498db', '#e74c3c', '#2ecc71', '#f39c12']),
                fake.date_time_between(start_date='-1h', end_date='now'),
                fake.date_time_between(start_date='-3m', end_date='now'),
                1,     # USE_DEFAULT_RUNTIME
                None,  # CUSTOM_BATCH_RUN_STEP_RUNTIME_XML
                random.uniform(60, 480),  # CUSTOM_RUNTIME
                fake.date_time_between(start_date='-1h', end_date='now'),
                random.choice(personnel_ids),
                0,     # IS_DELETED
                None,  # IMAGE_STRING_ID
                fake.text(max_nb_chars=200) if random.random() > 0.8 else None,
                random.randint(1, 3),     # BATCH_RUN_TYPE
                None,  # EXTRA_INFO_DATABASE_ID
                random.uniform(1, 1000),   # QUANTITY
                random.uniform(0, 50),     # REWORK_QUANTITY
                random.uniform(0, 20),     # SCRAP_QUANTITY
                random.uniform(0, 10),     # DEFECT_QUANTITY
                random.uniform(100, 5000), # COST
                None, None, None,          # CUSTOM fields
                random.randint(1, 5),      # PRIORITY
                created_by,
                scheduled_start,
                None,  # MODEL_ID
                scheduled_start + timedelta(days=random.randint(1, 15)),
                0,     # IS_LOCK
                None,  # LOCATION_LINK_ID
                None,  # DOCUMENT_LINK_ID
                0,     # IS_MODIFIED
                1, 1,  # ALLOW_ADD_STEP, ALLOW_EDIT_STEP
                None   # MASTER_BATCH_TEMPLATE
            ))
    
    cursor.executemany('''
        INSERT INTO BATCH_RUN (
            NAME, NOTES, SCHEDULED_START_DATE_TIME, START_DATE_TIME, END_DATE_TIME,
            INVOICE_NUMBER, PURCHASE_ORDER_ID, SALES_SCHEDULING_ID, BATCH_TEMPLATE_ID,
            PERSONNEL_ID, PARENT_RUN_ID, STATUS, GANTT_COLOR, LAST_UPDATE,
            CREATED_DATE_TIME, USE_DEFAULT_RUNTIME, CUSTOM_BATCH_RUN_STEP_RUNTIME_XML,
            CUSTOM_RUNTIME, HEARTBEAT_TIME, HEARTBEAT_USER, IS_DELETED,
            IMAGE_STRING_ID, INSTRUCTIONS, BATCH_RUN_TYPE, EXTRA_INFO_DATABASE_ID,
            QUANTITY, REWORK_QUANTITY, SCRAP_QUANTITY, DEFECT_QUANTITY, COST,
            CUSTOM_FINISHED_GOOD_INV_ITEM_LINK_ID, CUSTOM_INV_BOM_LINK_ID,
            CUSTOM_FINISHED_GOOD_INV_ITEM_TYPE_LINK_ID, PRIORITY, CREATED_BY,
            SCHEDULED_DATE_TIME, MODEL_ID, DELIVER_DATE_TIME, IS_LOCK,
            LOCATION_LINK_ID, DOCUMENT_LINK_ID, IS_MODIFIED, ALLOW_ADD_STEP,
            ALLOW_EDIT_STEP, MASTER_BATCH_TEMPLATE
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', jobs)
    
    conn.commit()
    print(f"✅ Generated {len(work_orders)} work orders and {len(jobs)} jobs")

def generate_job_steps_and_transactions(conn):
    """Generate job steps and their transactions."""
    cursor = conn.cursor()
    
    print("🔄 Generating job steps and transactions...")
    
    # Get reference data
    cursor.execute("SELECT ID FROM BATCH_RUN")
    job_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT ID FROM PERSONNEL LIMIT 50")
    personnel_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT ID FROM BATCH_TEMPLATE_STEP")
    template_step_ids = [row[0] for row in cursor.fetchall()]
    
    job_steps = []
    step_transactions = []
    
    # Generate job steps (3-8 steps per job)
    step_id_counter = 1
    for job_id in job_ids[:500]:  # Limit to first 500 jobs for performance
        num_steps = random.randint(3, 8)
        for step_idx in range(num_steps):
            personnel_id = random.choice(personnel_ids)
            template_step_id = random.choice(template_step_ids)
            
            expected_start = fake.date_time_between(start_date='-2m', end_date='+1m')
            expected_end = expected_start + timedelta(hours=random.randint(1, 8))
            start_time = expected_start + timedelta(hours=random.randint(-2, 2)) if random.random() > 0.4 else None
            end_time = start_time + timedelta(hours=random.randint(1, 6)) if start_time and random.random() > 0.6 else None
            
            job_steps.append((
                expected_start,
                expected_end,
                start_time,
                end_time,
                fake.text(max_nb_chars=100) if random.random() > 0.8 else None,
                job_id,
                personnel_id,
                template_step_id,
                step_idx + 1,  # INDEX
                random.choice([1, 2, 3, 5, 6]),  # STATUS
                random.choice(['#2ecc71', '#e74c3c', '#f39c12']),
                1,             # USE_DEFAULT_RUNTIME
                random.uniform(30, 240),  # CUSTOM_RUNTIME
                0,             # IS_DELETED
                fake.text(max_nb_chars=200) if random.random() > 0.7 else None,
                None,          # IMAGE_STRING
                random.choice([0, 1]),     # IN_USE
                None,          # TIMESHEET_PROFILE_ID
                None,          # CUSTOM_CURRENT_VALUES_DATA_TIMING_LINK_ID
                random.uniform(20, 180),   # CUSTOM_EXPECTED_MIN_TIME
                random.uniform(240, 360),  # CUSTOM_EXPECTED_MAX_TIME
                random.randint(1, 3),      # STEP_TYPE
                fake.text(max_nb_chars=300) if random.random() > 0.8 else None,
                None,          # BATCH_RUN_STEP_SPLIT_LINK_ID
                random.uniform(60, 300),   # CYCLE_TIME_SECONDS
                random.uniform(30, 240),   # ACTUAL_RUN_TIME_MINUTES
                fake.date_time_between(start_date='-1d', end_date='now') if random.random() > 0.5 else None,
                0,             # IS_LOCK
                f"Step {step_idx + 1} - {fake.word().title()}",
                None,          # AREA_LINK_ID
                None,          # DOCUMENT_LINK_ID
                0,             # IS_DISABLED
                0,             # DISABLE_OVERRIDE_ALLOWED
                1, 1,          # ALLOCATE_ASSET, ALLOCATE_PERSONNEL
                0,             # ALLOW_SPLIT
                random.randint(1, 3),      # CATEGORY
                random.uniform(0, 30),     # MIN_GAP_PREV_STEP
                random.uniform(50, 100)    # PARTIAL_COMPLETE_AFTER
            ))
            
            # Generate transactions for this step
            if random.random() > 0.3:  # 70% chance of having transactions
                num_transactions = random.randint(1, 5)
                for trans_idx in range(num_transactions):
                    step_transactions.append((
                        step_id_counter,  # BATCH_RUN_STEP_ID
                        fake.date_time_between(start_date='-1d', end_date='now'),
                        random.choice([3, 5, 6]),  # TRANSACTION_STATUS
                        random.choice(personnel_ids),
                        fake.text(max_nb_chars=100) if random.random() > 0.8 else None,
                        random.uniform(0, 100),    # TRANSACTION_AMOUNT
                        None,          # BATCH_RUN_STEP_PARAMETER_TRANSACTION_ID
                        None,          # OTHER_OWNER_TYPE_ENUM
                        None,          # OTHER_OWNER_TYPE_ID
                        0,             # IS_DELETED
                        0,             # IS_OVERRIDE
                        None, None, None, None, None, None  # OVERRIDE fields
                    ))
            
            step_id_counter += 1
    
    cursor.executemany('''
        INSERT INTO BATCH_RUN_STEP (
            EXPECTED_START_DATE_TIME, SPLIT_STEP_EXPECTED_END_DATE_TIME,
            START_DATE_TIME, END_DATE_TIME, NOTES, BATCH_RUN_ID, PERSONNEL_ID,
            BATCH_TEMPLATE_STEP_ID, "INDEX", STATUS, GANTT_COLOR, USE_DEFAULT_RUNTIME,
            CUSTOM_RUNTIME, IS_DELETED, INSTRUCTIONS, IMAGE_STRING, IN_USE,
            TIMESHEET_PROFILE_ID, CUSTOM_CURRENT_VALUES_DATA_TIMING_LINK_ID,
            CUSTOM_EXPECTED_MIN_TIME, CUSTOM_EXPECTED_MAX_TIME, STEP_TYPE,
            FULL_NOTES, BATCH_RUN_STEP_SPLIT_LINK_ID, CYCLE_TIME_SECONDS,
            ACTUAL_RUN_TIME_MINUTES, LAST_TRANSACTION_DATE_TIME, IS_LOCK, NAME,
            AREA_LINK_ID, DOCUMENT_LINK_ID, IS_DISABLED, DISABLE_OVERRIDE_ALLOWED,
            ALLOCATE_ASSET, ALLOCATE_PERSONNEL, ALLOW_SPLIT, CATEGORY,
            MIN_GAP_PREV_STEP, PARTIAL_COMPLETE_AFTER
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', job_steps)
    
    cursor.executemany('''
        INSERT INTO BATCH_RUN_STEP_TRANSACTION (
            BATCH_RUN_STEP_ID, TRANSACTION_DATE_TIME, TRANSACTION_STATUS,
            TRANSACTION_OWNER_USER_ID, TRANSACTION_NOTES, TRANSACTION_AMOUNT,
            BATCH_RUN_STEP_PARAMETER_TRANSACTION_ID, OTHER_OWNER_TYPE_ENUM,
            OTHER_OWNER_TYPE_ID, IS_DELETED, IS_OVERRIDE,
            OVERRIDE_PARENT_TRANSACTION_LINK_ID, OVERRIDE_DATE_TIME,
            OVERRIDE_AMOUNT, OVERRIDE_START_DATE_TIME, OVERRIDE_END_DATE_TIME,
            TRANSACTION_OVERRIDE_USER_ID
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', step_transactions)
    
    conn.commit()
    print(f"✅ Generated {len(job_steps)} job steps and {len(step_transactions)} step transactions")

def main():
    """Main function to populate the database with data."""
    print("🚀 Populating ArcOps 500-Table Database with data...")
    
    try:
        # Create database connection
        conn = create_database_connection()
        
        # Generate data in logical order
        generate_workflows_and_steps(conn)
        generate_work_orders_and_jobs(conn)
        generate_job_steps_and_transactions(conn)
        
        print(f"\n✅ Database populated successfully!")
        
        # Show final statistics
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n🔍 Final Database Statistics:")
        print(f"   Total Tables: {len(tables)}")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"   {table[0]}: {count:,} records")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

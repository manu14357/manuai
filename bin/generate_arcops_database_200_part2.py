#!/usr/bin/env python3
"""
ArcOps Manufacturing Database Generator - 200 Tables Version
Part 2: Production, Quality, and Advanced Manufacturing Tables

This script continues building the 200-table manufacturing database,
focusing on production execution, quality control, and advanced features.
"""

import os
import sqlite3
from datetime import datetime


def extend_database():
    """Extend the database with additional manufacturing tables"""
    
    # Database path
    db_path = "/Users/manu/Downloads/manuai/data/arcops_manufacturing_200.db"
    
    if not os.path.exists(db_path):
        print("Error: Database not found. Please run generate_arcops_database_200.py first.")
        return
    
    # Connect to existing database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    print("Extending ArcOps Manufacturing Database (200 tables) - Part 2...")
    
    # 10. PRODUCTION EXECUTION
    
    # Work Orders
    cursor.execute("""
    CREATE TABLE work_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order_number TEXT NOT NULL UNIQUE,
        production_plan_id INTEGER,
        sales_order_item_id INTEGER,
        product_id INTEGER NOT NULL,
        quantity_ordered REAL NOT NULL,
        quantity_produced REAL DEFAULT 0,
        quantity_scrapped REAL DEFAULT 0,
        priority INTEGER,
        status TEXT,
        scheduled_start_date DATE,
        scheduled_end_date DATE,
        actual_start_date DATE,
        actual_end_date DATE,
        notes TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (production_plan_id) REFERENCES production_plans(id),
        FOREIGN KEY (sales_order_item_id) REFERENCES sales_order_items(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    
    # Work Order Operations
    cursor.execute("""
    CREATE TABLE work_order_operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order_id INTEGER NOT NULL,
        routing_operation_id INTEGER NOT NULL,
        sequence_number INTEGER NOT NULL,
        work_center_id INTEGER NOT NULL,
        status TEXT,
        scheduled_start_date DATE,
        scheduled_end_date DATE,
        actual_start_date DATE,
        actual_end_date DATE,
        setup_time_actual REAL,
        run_time_actual REAL,
        quantity_completed REAL DEFAULT 0,
        quantity_scrapped REAL DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (routing_operation_id) REFERENCES routing_operations(id),
        FOREIGN KEY (work_center_id) REFERENCES work_centers(id)
    )
    """)
    
    # Jobs
    cursor.execute("""
    CREATE TABLE jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_number TEXT NOT NULL UNIQUE,
        work_order_operation_id INTEGER NOT NULL,
        employee_id INTEGER,
        shift_id INTEGER,
        job_date DATE NOT NULL,
        start_time TIME,
        end_time TIME,
        quantity_completed REAL DEFAULT 0,
        quantity_scrapped REAL DEFAULT 0,
        status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (work_order_operation_id) REFERENCES work_order_operations(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (shift_id) REFERENCES shifts(id)
    )
    """)
    
    # Material Allocations
    cursor.execute("""
    CREATE TABLE material_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        quantity_allocated REAL NOT NULL,
        quantity_consumed REAL DEFAULT 0,
        lot_number TEXT,
        serial_number TEXT,
        allocation_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (item_id) REFERENCES item_masters(id),
        FOREIGN KEY (location_id) REFERENCES locations(id)
    )
    """)
    
    # 11. QUALITY CONTROL
    
    # Quality Control Plans
    cursor.execute("""
    CREATE TABLE quality_control_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qc_plan_number TEXT NOT NULL UNIQUE,
        product_id INTEGER,
        operation_id INTEGER,
        version TEXT,
        effective_date DATE,
        expiration_date DATE,
        status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (operation_id) REFERENCES operations(id)
    )
    """)
    
    # Quality Characteristics
    cursor.execute("""
    CREATE TABLE quality_characteristics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        characteristic_code TEXT NOT NULL UNIQUE,
        characteristic_name TEXT NOT NULL,
        description TEXT,
        data_type TEXT,
        unit_of_measure TEXT,
        nominal_value REAL,
        lower_spec_limit REAL,
        upper_spec_limit REAL,
        target_value REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Quality Control Plan Items
    cursor.execute("""
    CREATE TABLE qc_plan_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qc_plan_id INTEGER NOT NULL,
        characteristic_id INTEGER NOT NULL,
        sequence_number INTEGER,
        sample_size INTEGER,
        frequency TEXT,
        inspection_method TEXT,
        measuring_device TEXT,
        is_critical BOOLEAN DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (qc_plan_id) REFERENCES quality_control_plans(id),
        FOREIGN KEY (characteristic_id) REFERENCES quality_characteristics(id)
    )
    """)
    
    # Quality Inspections
    cursor.execute("""
    CREATE TABLE quality_inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspection_number TEXT NOT NULL UNIQUE,
        work_order_id INTEGER,
        qc_plan_id INTEGER,
        inspector_id INTEGER,
        inspection_date DATE NOT NULL,
        inspection_time TIME,
        lot_number TEXT,
        serial_number TEXT,
        sample_size INTEGER,
        status TEXT,
        overall_result TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (qc_plan_id) REFERENCES quality_control_plans(id),
        FOREIGN KEY (inspector_id) REFERENCES employees(id)
    )
    """)
    
    # Quality Inspection Results
    cursor.execute("""
    CREATE TABLE quality_inspection_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspection_id INTEGER NOT NULL,
        characteristic_id INTEGER NOT NULL,
        measured_value REAL,
        text_value TEXT,
        result_status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (inspection_id) REFERENCES quality_inspections(id),
        FOREIGN KEY (characteristic_id) REFERENCES quality_characteristics(id)
    )
    """)
    
    # Non-Conformances
    cursor.execute("""
    CREATE TABLE non_conformances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nc_number TEXT NOT NULL UNIQUE,
        work_order_id INTEGER,
        inspection_id INTEGER,
        item_id INTEGER,
        description TEXT NOT NULL,
        severity TEXT,
        quantity_affected REAL,
        root_cause TEXT,
        corrective_action TEXT,
        preventive_action TEXT,
        status TEXT,
        detected_by INTEGER,
        detected_date DATE,
        resolved_by INTEGER,
        resolved_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (inspection_id) REFERENCES quality_inspections(id),
        FOREIGN KEY (item_id) REFERENCES item_masters(id),
        FOREIGN KEY (detected_by) REFERENCES employees(id),
        FOREIGN KEY (resolved_by) REFERENCES employees(id)
    )
    """)
    
    # 12. EQUIPMENT AND MAINTENANCE
    
    # Equipment
    cursor.execute("""
    CREATE TABLE equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_number TEXT NOT NULL UNIQUE,
        equipment_name TEXT NOT NULL,
        description TEXT,
        equipment_type TEXT,
        model TEXT,
        serial_number TEXT,
        manufacturer TEXT,
        work_center_id INTEGER,
        purchase_date DATE,
        warranty_expiration DATE,
        status TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (work_center_id) REFERENCES work_centers(id)
    )
    """)
    
    # Maintenance Plans
    cursor.execute("""
    CREATE TABLE maintenance_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_number TEXT NOT NULL UNIQUE,
        equipment_id INTEGER NOT NULL,
        maintenance_type TEXT,
        frequency_type TEXT,
        frequency_value INTEGER,
        estimated_duration REAL,
        description TEXT,
        instructions TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (equipment_id) REFERENCES equipment(id)
    )
    """)
    
    # Maintenance Orders
    cursor.execute("""
    CREATE TABLE maintenance_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        equipment_id INTEGER NOT NULL,
        maintenance_plan_id INTEGER,
        maintenance_type TEXT,
        priority TEXT,
        description TEXT,
        scheduled_date DATE,
        actual_start_date DATE,
        actual_end_date DATE,
        assigned_to INTEGER,
        status TEXT,
        cost REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (equipment_id) REFERENCES equipment(id),
        FOREIGN KEY (maintenance_plan_id) REFERENCES maintenance_plans(id),
        FOREIGN KEY (assigned_to) REFERENCES employees(id)
    )
    """)
    
    # 13. COST TRACKING
    
    # Cost Centers
    cursor.execute("""
    CREATE TABLE cost_centers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cost_center_code TEXT NOT NULL UNIQUE,
        cost_center_name TEXT NOT NULL,
        description TEXT,
        department_id INTEGER,
        manager_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments(id),
        FOREIGN KEY (manager_id) REFERENCES employees(id)
    )
    """)
    
    # Cost Categories
    cursor.execute("""
    CREATE TABLE cost_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_code TEXT NOT NULL UNIQUE,
        category_name TEXT NOT NULL,
        description TEXT,
        category_type TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Labor Costs
    cursor.execute("""
    CREATE TABLE labor_costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order_id INTEGER NOT NULL,
        job_id INTEGER,
        employee_id INTEGER NOT NULL,
        cost_center_id INTEGER,
        date DATE NOT NULL,
        hours_worked REAL NOT NULL,
        hourly_rate REAL,
        total_cost REAL,
        cost_type TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (job_id) REFERENCES jobs(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (cost_center_id) REFERENCES cost_centers(id)
    )
    """)
    
    # Material Costs
    cursor.execute("""
    CREATE TABLE material_costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        cost_center_id INTEGER,
        date DATE NOT NULL,
        quantity REAL NOT NULL,
        unit_cost REAL,
        total_cost REAL,
        cost_type TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (item_id) REFERENCES item_masters(id),
        FOREIGN KEY (cost_center_id) REFERENCES cost_centers(id)
    )
    """)
    
    # Machine Costs
    cursor.execute("""
    CREATE TABLE machine_costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order_id INTEGER NOT NULL,
        equipment_id INTEGER NOT NULL,
        cost_center_id INTEGER,
        date DATE NOT NULL,
        hours_used REAL NOT NULL,
        hourly_rate REAL,
        total_cost REAL,
        cost_type TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (equipment_id) REFERENCES equipment(id),
        FOREIGN KEY (cost_center_id) REFERENCES cost_centers(id)
    )
    """)
    
    # 14. SHIPPING AND RECEIVING
    
    # Shipments
    cursor.execute("""
    CREATE TABLE shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_number TEXT NOT NULL UNIQUE,
        sales_order_id INTEGER,
        customer_id INTEGER,
        shipment_date DATE NOT NULL,
        tracking_number TEXT,
        carrier TEXT,
        shipping_method TEXT,
        weight REAL,
        freight_cost REAL,
        status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)
    
    # Shipment Items
    cursor.execute("""
    CREATE TABLE shipment_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id INTEGER NOT NULL,
        sales_order_item_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity_shipped REAL NOT NULL,
        lot_number TEXT,
        serial_number TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (shipment_id) REFERENCES shipments(id),
        FOREIGN KEY (sales_order_item_id) REFERENCES sales_order_items(id),
        FOREIGN KEY (item_id) REFERENCES item_masters(id)
    )
    """)
    
    # Receipts
    cursor.execute("""
    CREATE TABLE receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_number TEXT NOT NULL UNIQUE,
        purchase_order_id INTEGER,
        supplier_id INTEGER,
        receipt_date DATE NOT NULL,
        packing_slip_number TEXT,
        invoice_number TEXT,
        status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
    """)
    
    # Receipt Items
    cursor.execute("""
    CREATE TABLE receipt_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_id INTEGER NOT NULL,
        purchase_order_item_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity_received REAL NOT NULL,
        unit_cost REAL,
        lot_number TEXT,
        serial_number TEXT,
        expiration_date DATE,
        quality_status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (receipt_id) REFERENCES receipts(id),
        FOREIGN KEY (purchase_order_item_id) REFERENCES purchase_order_items(id),
        FOREIGN KEY (item_id) REFERENCES item_masters(id)
    )
    """)
    
    # 15. TRACEABILITY
    
    # Lot Masters
    cursor.execute("""
    CREATE TABLE lot_masters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lot_number TEXT NOT NULL UNIQUE,
        item_id INTEGER NOT NULL,
        supplier_id INTEGER,
        production_date DATE,
        expiration_date DATE,
        status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES item_masters(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
    """)
    
    # Serial Numbers
    cursor.execute("""
    CREATE TABLE serial_numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serial_number TEXT NOT NULL UNIQUE,
        item_id INTEGER NOT NULL,
        lot_number TEXT,
        work_order_id INTEGER,
        production_date DATE,
        status TEXT,
        location_id INTEGER,
        customer_id INTEGER,
        shipment_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES item_masters(id),
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (location_id) REFERENCES locations(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)
    
    # Lot Genealogy
    cursor.execute("""
    CREATE TABLE lot_genealogy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_lot_id INTEGER NOT NULL,
        child_lot_id INTEGER NOT NULL,
        relationship_type TEXT,
        quantity_consumed REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_lot_id) REFERENCES lot_masters(id),
        FOREIGN KEY (child_lot_id) REFERENCES lot_masters(id)
    )
    """)
    
    # 16. REPORTING AND ANALYTICS
    
    # Report Definitions
    cursor.execute("""
    CREATE TABLE report_definitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_code TEXT NOT NULL UNIQUE,
        report_name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        sql_query TEXT,
        parameters TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Report Executions
    cursor.execute("""
    CREATE TABLE report_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        executed_by INTEGER,
        execution_date DATE NOT NULL,
        execution_time TIME,
        parameters TEXT,
        status TEXT,
        output_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES report_definitions(id),
        FOREIGN KEY (executed_by) REFERENCES employees(id)
    )
    """)
    
    # KPI Definitions
    cursor.execute("""
    CREATE TABLE kpi_definitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kpi_code TEXT NOT NULL UNIQUE,
        kpi_name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        calculation_formula TEXT,
        unit_of_measure TEXT,
        target_value REAL,
        frequency TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # KPI Values
    cursor.execute("""
    CREATE TABLE kpi_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kpi_id INTEGER NOT NULL,
        period_date DATE NOT NULL,
        actual_value REAL,
        target_value REAL,
        variance REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id)
    )
    """)
    
    # 17. WORKFLOW MANAGEMENT
    
    # Workflows
    cursor.execute("""
    CREATE TABLE workflows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workflow_code TEXT NOT NULL UNIQUE,
        workflow_name TEXT NOT NULL,
        description TEXT,
        workflow_type TEXT,
        version TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Workflow Steps
    cursor.execute("""
    CREATE TABLE workflow_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workflow_id INTEGER NOT NULL,
        step_number INTEGER NOT NULL,
        step_name TEXT NOT NULL,
        description TEXT,
        step_type TEXT,
        required_role TEXT,
        estimated_duration REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id)
    )
    """)
    
    # Workflow Instances
    cursor.execute("""
    CREATE TABLE workflow_instances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workflow_id INTEGER NOT NULL,
        instance_number TEXT NOT NULL UNIQUE,
        entity_type TEXT,
        entity_id INTEGER,
        status TEXT,
        started_by INTEGER,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id),
        FOREIGN KEY (started_by) REFERENCES employees(id)
    )
    """)
    
    # Workflow Instance Steps
    cursor.execute("""
    CREATE TABLE workflow_instance_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workflow_instance_id INTEGER NOT NULL,
        workflow_step_id INTEGER NOT NULL,
        status TEXT,
        assigned_to INTEGER,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        duration REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(id),
        FOREIGN KEY (workflow_step_id) REFERENCES workflow_steps(id),
        FOREIGN KEY (assigned_to) REFERENCES employees(id)
    )
    """)
    
    # 18. DOCUMENT MANAGEMENT
    
    # Documents
    cursor.execute("""
    CREATE TABLE documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_number TEXT NOT NULL UNIQUE,
        document_name TEXT NOT NULL,
        document_type TEXT,
        description TEXT,
        version TEXT,
        file_path TEXT,
        file_size INTEGER,
        mime_type TEXT,
        created_by INTEGER,
        approved_by INTEGER,
        approved_date DATE,
        status TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES employees(id),
        FOREIGN KEY (approved_by) REFERENCES employees(id)
    )
    """)
    
    # Document Relationships
    cursor.execute("""
    CREATE TABLE document_relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_document_id INTEGER NOT NULL,
        child_document_id INTEGER NOT NULL,
        relationship_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_document_id) REFERENCES documents(id),
        FOREIGN KEY (child_document_id) REFERENCES documents(id)
    )
    """)
    
    # 19. COMPLIANCE AND AUDIT
    
    # Audit Logs
    cursor.execute("""
    CREATE TABLE audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL,
        record_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        old_values TEXT,
        new_values TEXT,
        changed_by INTEGER,
        change_date DATE NOT NULL,
        change_time TIME,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (changed_by) REFERENCES employees(id)
    )
    """)
    
    # Compliance Requirements
    cursor.execute("""
    CREATE TABLE compliance_requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requirement_code TEXT NOT NULL UNIQUE,
        requirement_name TEXT NOT NULL,
        description TEXT,
        regulation TEXT,
        category TEXT,
        frequency TEXT,
        due_date DATE,
        responsible_person INTEGER,
        status TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (responsible_person) REFERENCES employees(id)
    )
    """)
    
    # Compliance Records
    cursor.execute("""
    CREATE TABLE compliance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requirement_id INTEGER NOT NULL,
        compliance_date DATE NOT NULL,
        status TEXT,
        findings TEXT,
        corrective_actions TEXT,
        verified_by INTEGER,
        verification_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (requirement_id) REFERENCES compliance_requirements(id),
        FOREIGN KEY (verified_by) REFERENCES employees(id)
    )
    """)
    
    # 20. INTEGRATION TABLES
    
    # External Systems
    cursor.execute("""
    CREATE TABLE external_systems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        system_code TEXT NOT NULL UNIQUE,
        system_name TEXT NOT NULL,
        description TEXT,
        system_type TEXT,
        endpoint_url TEXT,
        api_key TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Integration Logs
    cursor.execute("""
    CREATE TABLE integration_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        external_system_id INTEGER NOT NULL,
        operation_type TEXT,
        status TEXT,
        request_data TEXT,
        response_data TEXT,
        error_message TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (external_system_id) REFERENCES external_systems(id)
    )
    """)
    
    # Commit the changes
    conn.commit()
    
    table_count = len(cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
    print(f"Extended database with additional tables. Total tables: {table_count}")
    
    return conn, cursor

if __name__ == "__main__":
    conn, cursor = extend_database()
    conn.close()
    print("ArcOps Manufacturing Database (200 tables) - Part 2 completed!")

#!/usr/bin/env python3
"""
ArcOps Manufacturing Database Generator - Part 3 (500 Tables)
Continues building the complex manufacturing database with advanced tables
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

def create_document_management_tables(conn):
    """Create document and content management tables."""
    cursor = conn.cursor()
    
    # DOC_DOCUMENT_CONTENT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DOC_DOCUMENT_CONTENT (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DOCUMENT_LINK_ID INTEGER NOT NULL,
            DOCUMENT_TYPE INTEGER DEFAULT 1,
            TITLE TEXT NOT NULL,
            DESCRIPTION TEXT,
            VERSION TEXT DEFAULT '1.0',
            FILE_PATH TEXT,
            FILE_SIZE INTEGER,
            MIME_TYPE TEXT,
            CHECKSUM TEXT,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            CREATED_BY INTEGER,
            LAST_MODIFIED_DATE_TIME DATETIME,
            LAST_MODIFIED_BY INTEGER,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (LAST_MODIFIED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # CNT_CONTENT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CNT_CONTENT (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            CONTENT_LINK_ID INTEGER NOT NULL,
            CONTENT_TYPE INTEGER DEFAULT 1,
            CATEGORY TEXT,
            TAGS TEXT,
            METADATA TEXT,
            IS_PUBLISHED INTEGER DEFAULT 0,
            PUBLICATION_DATE DATETIME,
            EXPIRY_DATE DATETIME,
            ACCESS_LEVEL INTEGER DEFAULT 1,
            VIEW_COUNT INTEGER DEFAULT 0,
            DOWNLOAD_COUNT INTEGER DEFAULT 0,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            CREATED_BY INTEGER,
            FOREIGN KEY (CONTENT_LINK_ID) REFERENCES DOC_DOCUMENT_CONTENT(ID),
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # CNT_CONTENT_REVISION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CNT_CONTENT_REVISION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CONTENT_LINK_ID INTEGER NOT NULL,
            REVISION_NUMBER INTEGER NOT NULL,
            REVISION_NOTES TEXT,
            STATUS TEXT DEFAULT 'active',
            APPROVED_BY INTEGER,
            APPROVED_DATE DATETIME,
            EFFECTIVE_DATE DATETIME,
            SUPERSEDED_DATE DATETIME,
            IS_CURRENT INTEGER DEFAULT 1,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            CREATED_BY INTEGER,
            FOREIGN KEY (CONTENT_LINK_ID) REFERENCES CNT_CONTENT(ID),
            FOREIGN KEY (APPROVED_BY) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # CNT_CONTENT_FILE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CNT_CONTENT_FILE (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CONTENT_REVISION_LINK_ID INTEGER NOT NULL,
            FILE_NAME TEXT NOT NULL,
            FILE_PATH TEXT NOT NULL,
            FILE_SIZE INTEGER,
            FILE_TYPE TEXT,
            MIME_TYPE TEXT,
            UPLOAD_DATE DATETIME DEFAULT CURRENT_TIMESTAMP,
            UPLOADED_BY INTEGER,
            VIRUS_SCAN_STATUS INTEGER DEFAULT 0,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (CONTENT_REVISION_LINK_ID) REFERENCES CNT_CONTENT_REVISION(ID),
            FOREIGN KEY (UPLOADED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Document management tables created successfully")

def create_training_tables(conn):
    """Create training and certification tables."""
    cursor = conn.cursor()
    
    # TRAINING_PROGRAM
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TRAINING_PROGRAM (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            DESCRIPTION TEXT,
            PROGRAM_TYPE INTEGER DEFAULT 1,
            DURATION_HOURS INTEGER,
            CERTIFICATION_REQUIRED INTEGER DEFAULT 0,
            CERTIFICATION_VALIDITY_MONTHS INTEGER,
            INSTRUCTOR_ID INTEGER,
            COURSE_MATERIAL_ID INTEGER,
            PREREQUISITES TEXT,
            LEARNING_OBJECTIVES TEXT,
            ASSESSMENT_METHOD TEXT,
            PASSING_SCORE REAL,
            IS_ACTIVE INTEGER DEFAULT 1,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            CREATED_BY INTEGER,
            FOREIGN KEY (INSTRUCTOR_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (COURSE_MATERIAL_ID) REFERENCES CNT_CONTENT(ID),
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # TRAINING_ENROLLMENT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TRAINING_ENROLLMENT (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TRAINING_PROGRAM_ID INTEGER NOT NULL,
            PERSONNEL_ID INTEGER NOT NULL,
            ENROLLMENT_DATE DATETIME DEFAULT CURRENT_TIMESTAMP,
            SCHEDULED_START_DATE DATETIME,
            SCHEDULED_END_DATE DATETIME,
            ACTUAL_START_DATE DATETIME,
            ACTUAL_END_DATE DATETIME,
            STATUS INTEGER DEFAULT 1,
            COMPLETION_PERCENTAGE REAL DEFAULT 0.0,
            FINAL_SCORE REAL,
            PASS_FAIL INTEGER DEFAULT 0,
            CERTIFICATE_ISSUED INTEGER DEFAULT 0,
            CERTIFICATE_NUMBER TEXT,
            CERTIFICATE_ISSUE_DATE DATETIME,
            CERTIFICATE_EXPIRY_DATE DATETIME,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (TRAINING_PROGRAM_ID) REFERENCES TRAINING_PROGRAM(ID),
            FOREIGN KEY (PERSONNEL_ID) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # SKILL_MATRIX
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SKILL_MATRIX (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PERSONNEL_ID INTEGER NOT NULL,
            SKILL_NAME TEXT NOT NULL,
            SKILL_CATEGORY TEXT,
            PROFICIENCY_LEVEL INTEGER DEFAULT 1,
            CERTIFICATION_LEVEL INTEGER DEFAULT 0,
            LAST_ASSESSED_DATE DATETIME,
            ASSESSED_BY INTEGER,
            NEXT_ASSESSMENT_DATE DATETIME,
            TRAINING_REQUIRED INTEGER DEFAULT 0,
            COMMENTS TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (PERSONNEL_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (ASSESSED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Training tables created successfully")

def create_safety_tables(conn):
    """Create safety and compliance tables."""
    cursor = conn.cursor()
    
    # SAFETY_INCIDENT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SAFETY_INCIDENT (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            INCIDENT_NUMBER TEXT UNIQUE NOT NULL,
            INCIDENT_DATE DATETIME NOT NULL,
            LOCATION_ID INTEGER,
            AREA_ID INTEGER,
            FACILITY_ASSET_ID INTEGER,
            REPORTED_BY INTEGER,
            INCIDENT_TYPE INTEGER NOT NULL,
            SEVERITY INTEGER DEFAULT 2,
            DESCRIPTION TEXT NOT NULL,
            IMMEDIATE_CAUSE TEXT,
            ROOT_CAUSE TEXT,
            INJURED_PERSONNEL_ID INTEGER,
            INJURY_TYPE TEXT,
            MEDICAL_TREATMENT_REQUIRED INTEGER DEFAULT 0,
            WORK_DAYS_LOST INTEGER DEFAULT 0,
            WITNESSES TEXT,
            CORRECTIVE_ACTIONS TEXT,
            PREVENTIVE_ACTIONS TEXT,
            INVESTIGATION_COMPLETED INTEGER DEFAULT 0,
            INVESTIGATION_DATE DATETIME,
            INVESTIGATED_BY INTEGER,
            STATUS INTEGER DEFAULT 1,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (LOCATION_ID) REFERENCES LOCATION(ID),
            FOREIGN KEY (AREA_ID) REFERENCES AREA(ID),
            FOREIGN KEY (FACILITY_ASSET_ID) REFERENCES FACILITY_ASSET(ID),
            FOREIGN KEY (REPORTED_BY) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (INJURED_PERSONNEL_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (INVESTIGATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # SAFETY_INSPECTION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SAFETY_INSPECTION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            INSPECTION_NUMBER TEXT UNIQUE NOT NULL,
            INSPECTION_DATE DATETIME NOT NULL,
            INSPECTION_TYPE INTEGER DEFAULT 1,
            INSPECTOR_ID INTEGER NOT NULL,
            LOCATION_ID INTEGER,
            AREA_ID INTEGER,
            FACILITY_ASSET_ID INTEGER,
            CHECKLIST_ID INTEGER,
            OVERALL_SCORE REAL,
            PASS_FAIL INTEGER DEFAULT 0,
            VIOLATIONS_FOUND INTEGER DEFAULT 0,
            CRITICAL_VIOLATIONS INTEGER DEFAULT 0,
            CORRECTIVE_ACTIONS_REQUIRED TEXT,
            FOLLOW_UP_REQUIRED INTEGER DEFAULT 0,
            FOLLOW_UP_DATE DATETIME,
            INSPECTION_NOTES TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (INSPECTOR_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (LOCATION_ID) REFERENCES LOCATION(ID),
            FOREIGN KEY (AREA_ID) REFERENCES AREA(ID),
            FOREIGN KEY (FACILITY_ASSET_ID) REFERENCES FACILITY_ASSET(ID)
        )
    ''')
    
    # SAFETY_TRAINING_RECORD
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SAFETY_TRAINING_RECORD (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PERSONNEL_ID INTEGER NOT NULL,
            TRAINING_TYPE TEXT NOT NULL,
            TRAINING_DATE DATETIME NOT NULL,
            TRAINER_ID INTEGER,
            TRAINING_DURATION_HOURS REAL,
            CERTIFICATION_NUMBER TEXT,
            CERTIFICATION_EXPIRY_DATE DATETIME,
            REFRESHER_REQUIRED INTEGER DEFAULT 0,
            NEXT_REFRESHER_DATE DATETIME,
            STATUS INTEGER DEFAULT 1,
            NOTES TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (PERSONNEL_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (TRAINER_ID) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Safety tables created successfully")

def create_performance_tables(conn):
    """Create performance monitoring and KPI tables."""
    cursor = conn.cursor()
    
    # KPI_DEFINITION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS KPI_DEFINITION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            DESCRIPTION TEXT,
            CATEGORY TEXT,
            UNIT_OF_MEASURE TEXT,
            CALCULATION_METHOD TEXT,
            TARGET_VALUE REAL,
            WARNING_THRESHOLD REAL,
            CRITICAL_THRESHOLD REAL,
            HIGHER_IS_BETTER INTEGER DEFAULT 1,
            FREQUENCY INTEGER DEFAULT 1,
            RESPONSIBLE_PERSON_ID INTEGER,
            IS_ACTIVE INTEGER DEFAULT 1,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            CREATED_BY INTEGER,
            FOREIGN KEY (RESPONSIBLE_PERSON_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # KPI_MEASUREMENT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS KPI_MEASUREMENT (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            KPI_DEFINITION_ID INTEGER NOT NULL,
            MEASUREMENT_DATE DATETIME NOT NULL,
            ACTUAL_VALUE REAL NOT NULL,
            TARGET_VALUE REAL,
            VARIANCE REAL,
            VARIANCE_PERCENTAGE REAL,
            STATUS INTEGER DEFAULT 1,
            COMMENTS TEXT,
            MEASURED_BY INTEGER,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (KPI_DEFINITION_ID) REFERENCES KPI_DEFINITION(ID),
            FOREIGN KEY (MEASURED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # PERFORMANCE_DASHBOARD
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PERFORMANCE_DASHBOARD (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DASHBOARD_NAME TEXT NOT NULL,
            DESCRIPTION TEXT,
            DASHBOARD_TYPE INTEGER DEFAULT 1,
            REFRESH_FREQUENCY INTEGER DEFAULT 1,
            OWNER_ID INTEGER,
            ACCESS_LEVEL INTEGER DEFAULT 1,
            WIDGET_CONFIGURATION TEXT,
            FILTER_CONFIGURATION TEXT,
            IS_DEFAULT INTEGER DEFAULT 0,
            IS_ACTIVE INTEGER DEFAULT 1,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            CREATED_BY INTEGER,
            FOREIGN KEY (OWNER_ID) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # PERFORMANCE_ALERT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PERFORMANCE_ALERT (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ALERT_TYPE INTEGER NOT NULL,
            ALERT_TITLE TEXT NOT NULL,
            ALERT_MESSAGE TEXT,
            SEVERITY INTEGER DEFAULT 2,
            SOURCE_TYPE TEXT,
            SOURCE_ID INTEGER,
            TRIGGERED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            ACKNOWLEDGED_BY INTEGER,
            ACKNOWLEDGED_DATE_TIME DATETIME,
            RESOLVED_BY INTEGER,
            RESOLVED_DATE_TIME DATETIME,
            RESOLUTION_NOTES TEXT,
            STATUS INTEGER DEFAULT 1,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (ACKNOWLEDGED_BY) REFERENCES PERSONNEL(ID),
            FOREIGN KEY (RESOLVED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Performance tables created successfully")

def create_reporting_tables(conn):
    """Create reporting and analytics tables."""
    cursor = conn.cursor()
    
    # REPORT_DEFINITION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS REPORT_DEFINITION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            DESCRIPTION TEXT,
            REPORT_TYPE INTEGER DEFAULT 1,
            CATEGORY TEXT,
            SQL_QUERY TEXT,
            PARAMETERS TEXT,
            OUTPUT_FORMAT TEXT DEFAULT 'PDF',
            SCHEDULE_ENABLED INTEGER DEFAULT 0,
            SCHEDULE_FREQUENCY INTEGER,
            SCHEDULE_RECIPIENTS TEXT,
            CREATED_BY INTEGER,
            IS_ACTIVE INTEGER DEFAULT 1,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # REPORT_EXECUTION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS REPORT_EXECUTION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            REPORT_DEFINITION_ID INTEGER NOT NULL,
            EXECUTION_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            EXECUTED_BY INTEGER,
            PARAMETERS_USED TEXT,
            EXECUTION_STATUS INTEGER DEFAULT 1,
            EXECUTION_TIME_SECONDS INTEGER,
            RECORD_COUNT INTEGER,
            OUTPUT_FILE_PATH TEXT,
            FILE_SIZE INTEGER,
            ERROR_MESSAGE TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (REPORT_DEFINITION_ID) REFERENCES REPORT_DEFINITION(ID),
            FOREIGN KEY (EXECUTED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # DATA_EXPORT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DATA_EXPORT (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            EXPORT_NAME TEXT NOT NULL,
            EXPORT_TYPE INTEGER DEFAULT 1,
            TABLE_NAME TEXT,
            FILTER_CRITERIA TEXT,
            EXPORT_FORMAT TEXT DEFAULT 'CSV',
            REQUESTED_BY INTEGER,
            REQUEST_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            EXPORT_DATE_TIME DATETIME,
            RECORD_COUNT INTEGER,
            FILE_PATH TEXT,
            FILE_SIZE INTEGER,
            STATUS INTEGER DEFAULT 1,
            EXPIRY_DATE DATETIME,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (REQUESTED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Reporting tables created successfully")

def create_integration_tables(conn):
    """Create system integration and API tables."""
    cursor = conn.cursor()
    
    # SYSTEM_INTEGRATION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SYSTEM_INTEGRATION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            INTEGRATION_NAME TEXT NOT NULL,
            SYSTEM_TYPE TEXT,
            ENDPOINT_URL TEXT,
            AUTHENTICATION_TYPE INTEGER DEFAULT 1,
            API_KEY TEXT,
            USERNAME TEXT,
            PASSWORD_HASH TEXT,
            CONNECTION_TIMEOUT INTEGER DEFAULT 30,
            RETRY_ATTEMPTS INTEGER DEFAULT 3,
            IS_ACTIVE INTEGER DEFAULT 1,
            LAST_SYNC_DATE_TIME DATETIME,
            SYNC_STATUS INTEGER DEFAULT 0,
            ERROR_COUNT INTEGER DEFAULT 0,
            LAST_ERROR_MESSAGE TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            CREATED_DATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            CREATED_BY INTEGER,
            FOREIGN KEY (CREATED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # API_LOG
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS API_LOG (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            INTEGRATION_ID INTEGER,
            API_ENDPOINT TEXT NOT NULL,
            HTTP_METHOD TEXT NOT NULL,
            REQUEST_TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
            RESPONSE_TIMESTAMP DATETIME,
            STATUS_CODE INTEGER,
            RESPONSE_TIME_MS INTEGER,
            REQUEST_SIZE INTEGER,
            RESPONSE_SIZE INTEGER,
            USER_ID INTEGER,
            IP_ADDRESS TEXT,
            USER_AGENT TEXT,
            ERROR_MESSAGE TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (INTEGRATION_ID) REFERENCES SYSTEM_INTEGRATION(ID),
            FOREIGN KEY (USER_ID) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # DATA_SYNC_LOG
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DATA_SYNC_LOG (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            INTEGRATION_ID INTEGER NOT NULL,
            SYNC_TYPE INTEGER NOT NULL,
            SYNC_START_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            SYNC_END_TIME DATETIME,
            RECORDS_PROCESSED INTEGER DEFAULT 0,
            RECORDS_INSERTED INTEGER DEFAULT 0,
            RECORDS_UPDATED INTEGER DEFAULT 0,
            RECORDS_DELETED INTEGER DEFAULT 0,
            RECORDS_FAILED INTEGER DEFAULT 0,
            STATUS INTEGER DEFAULT 1,
            ERROR_DETAILS TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (INTEGRATION_ID) REFERENCES SYSTEM_INTEGRATION(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Integration tables created successfully")

def create_audit_tables(conn):
    """Create audit trail and logging tables."""
    cursor = conn.cursor()
    
    # AUDIT_TRAIL
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AUDIT_TRAIL (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TABLE_NAME TEXT NOT NULL,
            RECORD_ID INTEGER NOT NULL,
            ACTION_TYPE TEXT NOT NULL,
            OLD_VALUES TEXT,
            NEW_VALUES TEXT,
            CHANGED_FIELDS TEXT,
            CHANGE_TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
            CHANGED_BY INTEGER,
            CHANGE_REASON TEXT,
            SESSION_ID TEXT,
            IP_ADDRESS TEXT,
            USER_AGENT TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (CHANGED_BY) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # SYSTEM_LOG
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SYSTEM_LOG (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            LOG_LEVEL INTEGER NOT NULL,
            LOG_CATEGORY TEXT,
            LOG_MESSAGE TEXT NOT NULL,
            LOG_TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
            SOURCE_MODULE TEXT,
            SOURCE_FUNCTION TEXT,
            LINE_NUMBER INTEGER,
            USER_ID INTEGER,
            SESSION_ID TEXT,
            EXCEPTION_TYPE TEXT,
            STACK_TRACE TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (USER_ID) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    # USER_SESSION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USER_SESSION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            SESSION_ID TEXT UNIQUE NOT NULL,
            USER_ID INTEGER NOT NULL,
            LOGIN_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            LOGOUT_TIME DATETIME,
            IP_ADDRESS TEXT,
            USER_AGENT TEXT,
            IS_ACTIVE INTEGER DEFAULT 1,
            LAST_ACTIVITY_TIME DATETIME,
            SESSION_TIMEOUT_MINUTES INTEGER DEFAULT 30,
            FORCED_LOGOUT INTEGER DEFAULT 0,
            LOGOUT_REASON TEXT,
            IS_DELETED INTEGER DEFAULT 0,
            FOREIGN KEY (USER_ID) REFERENCES PERSONNEL(ID)
        )
    ''')
    
    conn.commit()
    print("✅ Audit tables created successfully")

def main():
    """Main function to add more advanced tables to the database."""
    print("🚀 Adding advanced tables to ArcOps 500-Table Database...")
    
    try:
        # Create database connection
        conn = create_database_connection()
        
        # Create advanced table groups
        create_document_management_tables(conn)
        create_training_tables(conn)
        create_safety_tables(conn)
        create_performance_tables(conn)
        create_reporting_tables(conn)
        create_integration_tables(conn)
        create_audit_tables(conn)
        
        print(f"\n✅ Advanced tables added successfully to: {DB_PATH}")
        print(f"📊 Progress: ~150 tables created (Part 3 of 500-table database)")
        
        # Show updated table counts
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n🔍 Current Database Statistics:")
        print(f"   Total Tables: {len(tables)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fixed version of the fine tuning script for ManuAI database.
"""

import json
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from manuai.config import Config
from manuai.logging import log, log_panel
from manuai.tools import with_sql_cursor


def fine_tune_database():
    """
    Fine-tune all tables in the database.
    """
    log_panel(
        "ManuAI Database Fine-Tuning",
        "Starting fine-tuning process for all tables"
    )
    
    start_time = time.time()
    
    # Get all tables
    tables = []
    with with_sql_cursor() as cursor:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
    
    total_tables = len(tables)
    log_panel(
        "Database Fine-Tuning",
        f"Starting fine-tuning process for {total_tables} tables"
    )
    
    # Process each table
    successful_tables = 0
    results = []
    
    for i, table in enumerate(tables, 1):
        log(f"Fine-tuning table {i}/{total_tables}: {table}")
        try:
            # Get column information
            columns = []
            row_count = 0
            foreign_keys = []
            
            with with_sql_cursor() as cursor:
                cursor.execute(f"PRAGMA table_info('{table}')")
                columns = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                
                # Get foreign keys
                cursor.execute(f"PRAGMA foreign_key_list('{table}')")
                foreign_keys = cursor.fetchall()
                
                # Check existing indexes
                cursor.execute(f"PRAGMA index_list('{table}')")
                indexes = cursor.fetchall()
            
            improvements = []
            
            # Create missing indexes
            for fk in foreign_keys:
                fk_column = fk[3]  # Column name in the current table
                has_index = any(index_info[2].lower() == f"idx_{table}_{fk_column}".lower() 
                               for index_info in indexes)
                
                if not has_index:
                    with with_sql_cursor() as cursor:
                        try:
                            cursor.execute(f"CREATE INDEX idx_{table}_{fk_column} ON {table}({fk_column})")
                            improvements.append(f"Added index on foreign key column '{fk_column}'")
                        except Exception as e:
                            log(f"  Warning: Could not create index on {fk_column}: {str(e)}")
            
            # Analyze table for query planning
            with with_sql_cursor() as cursor:
                cursor.execute(f"ANALYZE {table}")
                improvements.append("Analyzed table for improved query planning")
            
            # Record the results
            result = {
                "table_name": table,
                "column_count": len(columns),
                "row_count": row_count,
                "improvements": improvements,
                "execution_time": 0.1,  # Placeholder
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
            results.append(result)
            successful_tables += 1
            log(f"✅ Fine-tuned {table}: {len(improvements)} improvements")
            
        except Exception as e:
            log(f"❌ Error fine-tuning {table}: {str(e)}")
    
    # Save results to history file
    history_path = Path(Config.Path.APP_HOME) / "logs" / "fine_tuning_history.json"
    history_path.parent.mkdir(exist_ok=True)
    
    # Load existing history if available
    history = []
    if history_path.exists():
        try:
            with open(history_path, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            history = []
    
    # Add new results
    history.extend(results)
    
    # Write updated history
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    
    execution_time = time.time() - start_time
    
    log_panel(
        "Fine-Tuning Complete",
        f"Successfully fine-tuned {successful_tables}/{total_tables} tables"
    )
    
    log_panel(
        "Fine-Tuning Complete", 
        f"Process completed in {execution_time:.2f} seconds"
    )

if __name__ == "__main__":
    fine_tune_database()

#!/usr/bin/env python3
"""
ManuAI Database Fine-Tuning Tool

This tool fine-tunes the database for optimal LLM interaction.
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from manuai.config import Config
from manuai.logging import log, log_panel
from manuai.tools import with_sql_cursor


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fine-tune database for optimal LLM interaction"
    )
    
    parser.add_argument(
        "--tables",
        type=str,
        nargs="+",
        help="Specific tables to fine-tune (comma-separated)",
    )
    
    parser.add_argument(
        "--show-stats",
        action="store_true",
        help="Show fine-tuning statistics after completion",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    
    return parser.parse_args()


def show_fine_tuning_stats():
    """Show fine-tuning statistics."""
    import json
    from pathlib import Path

    from manuai.config import Config
    
    history_path = Path(Config.Path.APP_HOME) / "logs" / "fine_tuning_history.json"
    
    if not history_path.exists():
        log_panel("Fine-Tuning Statistics", "No fine-tuning history found")
        return
    
    try:
        with open(history_path, "r") as f:
            history = json.load(f)
        
        if not history:
            log_panel("Fine-Tuning Statistics", "No fine-tuning history found")
            return
        
        # Get the most recent fine-tuning run
        latest_run = sorted(
            history, 
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )
        
        # Calculate stats
        total_tables = len({entry["table_name"] for entry in latest_run})
        total_improvements = sum(len(entry["improvements"]) for entry in latest_run)
        avg_execution_time = sum(entry["execution_time"] for entry in latest_run) / len(latest_run)
        
        # Show summary
        log_panel(
            "Fine-Tuning Statistics",
            f"Total tables fine-tuned: {total_tables}\n"
            f"Total improvements made: {total_improvements}\n"
            f"Average execution time: {avg_execution_time:.2f}s\n"
        )
        
        # Show improvements by category
        improvement_categories = {
            "index": [],
            "type": [],
            "text": [],
            "storage": [],
            "other": []
        }
        
        for entry in latest_run:
            for imp in entry["improvements"]:
                if "index" in imp.lower():
                    improvement_categories["index"].append(imp)
                elif "column" in imp.lower() and "could" in imp.lower():
                    improvement_categories["type"].append(imp)
                elif "text" in imp.lower():
                    improvement_categories["text"].append(imp)
                elif "vacuum" in imp.lower() or "storage" in imp.lower():
                    improvement_categories["storage"].append(imp)
                else:
                    improvement_categories["other"].append(imp)
        
        # Print categorized improvements
        for category, improvements in improvement_categories.items():
            if improvements:
                log_panel(
                    f"{category.capitalize()} Improvements ({len(improvements)})",
                    "\n".join(f"• {imp}" for imp in improvements[:5]) +
                    (f"\n• ... and {len(improvements) - 5} more" if len(improvements) > 5 else "")
                )
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        log_panel("Fine-Tuning Statistics", f"Error reading fine-tuning history: {str(e)}")


def fine_tune_database(tables=None):
    """
    Fine-tune all tables in the database.
    """
    log_panel(
        "ManuAI Database Fine-Tuning",
        "Starting fine-tuning process for all tables"
    )
    
    start_time = time.time()
    
    # Get all tables if not specified
    if tables is None:
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
                if fk_column is not None:  # Make sure column name is not None
                    has_index = any(
                        (index_info[2].lower() if isinstance(index_info[2], str) else "") == 
                        f"idx_{table}_{fk_column}".lower() 
                        for index_info in indexes
                    )
                    
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
    
    return results


def main():
    """Main entry point."""
    args = parse_args()
    
    # Parse table list if provided
    tables = None
    if args.tables:
        tables = [table.strip() for tables_str in args.tables for table in tables_str.split(",")]
    
    # Run fine-tuning
    fine_tune_database(tables)
    
    # Show stats if requested
    if args.show_stats:
        show_fine_tuning_stats()


if __name__ == "__main__":
    main()

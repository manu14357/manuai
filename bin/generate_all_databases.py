#!/usr/bin/env python3
"""
ArcOps Manufacturing Database Master Generation Script

This script runs all the database generation scripts in the correct order
to create both the 500-table and 200-table manufacturing databases.
"""

import os
import subprocess
import sys
import time
from datetime import datetime


def run_script(script_path, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"Starting: {description}")
    print(f"Script: {script_path}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    
    if not os.path.exists(script_path):
        print(f"ERROR: Script not found: {script_path}")
        return False
    
    try:
        start_time = time.time()
        
        # Run the script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"SUCCESS: {description} completed in {duration:.2f} seconds")
        print(f"Output: {result.stdout}")
        
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed with return code {e.returncode}")
        print(f"Error output: {e.stderr}")
        print(f"Standard output: {e.stdout}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error running {description}: {str(e)}")
        return False

def main():
    """Main function to run all database generation scripts"""
    print("ArcOps Manufacturing Database Master Generation Script")
    print("=" * 60)
    
    # Base directory
    base_dir = "/Users/manu/Downloads/manuai"
    bin_dir = os.path.join(base_dir, "bin")
    data_dir = os.path.join(base_dir, "data")
    
    # Ensure data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
    
    # Scripts to run in order
    scripts = [
        # 500-table database
        {
            "path": os.path.join(bin_dir, "generate_arcops_database_500.py"),
            "description": "Generate 500-table database (Part 1)"
        },
        {
            "path": os.path.join(bin_dir, "generate_arcops_database_500_part2.py"),
            "description": "Generate 500-table database (Part 2)"
        },
        {
            "path": os.path.join(bin_dir, "generate_arcops_database_500_part3.py"),
            "description": "Generate 500-table database (Part 3)"
        },
        {
            "path": os.path.join(bin_dir, "generate_arcops_data_500.py"),
            "description": "Populate 500-table database with data"
        },
        
        # 200-table database
        {
            "path": os.path.join(bin_dir, "generate_arcops_database_200.py"),
            "description": "Generate 200-table database (Part 1)"
        },
        {
            "path": os.path.join(bin_dir, "generate_arcops_database_200_part2.py"),
            "description": "Generate 200-table database (Part 2)"
        },
        {
            "path": os.path.join(bin_dir, "generate_arcops_data_200.py"),
            "description": "Populate 200-table database with data"
        }
    ]
    
    # Track results
    results = []
    total_start_time = time.time()
    
    # Run each script
    for script in scripts:
        success = run_script(script["path"], script["description"])
        results.append({
            "script": script["path"],
            "description": script["description"],
            "success": success
        })
        
        if not success:
            print(f"\nFAILED: Stopping execution due to failure in {script['description']}")
            break
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Print summary
    print(f"\n{'='*60}")
    print("EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total execution time: {total_duration:.2f} seconds")
    print(f"Scripts executed: {len(results)}")
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    print(f"\nDetailed Results:")
    for i, result in enumerate(results, 1):
        status = "✓ SUCCESS" if result["success"] else "✗ FAILED"
        print(f"{i:2d}. {status} - {result['description']}")
    
    if failed == 0:
        print(f"\n🎉 ALL SCRIPTS COMPLETED SUCCESSFULLY!")
        print(f"\nGenerated databases:")
        
        # Check if databases were created
        db_500_path = os.path.join(data_dir, "arcops_manufacturing_500.db")
        db_200_path = os.path.join(data_dir, "arcops_manufacturing_200.db")
        
        if os.path.exists(db_500_path):
            size_500 = os.path.getsize(db_500_path) / (1024 * 1024)  # MB
            print(f"- 500-table database: {db_500_path} ({size_500:.2f} MB)")
        
        if os.path.exists(db_200_path):
            size_200 = os.path.getsize(db_200_path) / (1024 * 1024)  # MB
            print(f"- 200-table database: {db_200_path} ({size_200:.2f} MB)")
        
        print(f"\nNext steps:")
        print(f"1. You can now connect to these databases using SQLite tools")
        print(f"2. Use the databases for testing, development, or demonstrations")
        print(f"3. Run SQL queries to explore the generated data")
        
    else:
        print(f"\n❌ SOME SCRIPTS FAILED!")
        print(f"Please check the error messages above and fix any issues.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

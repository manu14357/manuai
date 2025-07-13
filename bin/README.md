# ArcOps Manufacturing Database Generation Scripts

This directory contains scripts to generate large, complex manufacturing databases based on the ArcOps Manufacturing Execution System (MES) context.

## Overview

The scripts create two comprehensive manufacturing databases:
- **500-table database**: A large, enterprise-scale manufacturing database
- **200-table database**: A smaller but still comprehensive manufacturing database

Both databases are populated with realistic data using the Faker library.

## Files

### Database Generation Scripts

#### 500-Table Database
- `generate_arcops_database_500.py` - Core tables (customers, personnel, facility assets)
- `generate_arcops_database_500_part2.py` - Extended tables (inventory, quality, suppliers, maintenance)
- `generate_arcops_database_500_part3.py` - Advanced tables (documents, training, safety, reporting)
- `generate_arcops_data_500.py` - Populates the 500-table database with realistic data

#### 200-Table Database
- `generate_arcops_database_200.py` - Core manufacturing tables
- `generate_arcops_database_200_part2.py` - Production, quality, and advanced features
- `generate_arcops_data_200.py` - Populates the 200-table database with realistic data

#### Master Script
- `generate_all_databases.py` - Runs all scripts in correct order

## Usage

### Prerequisites

1. **Python 3.7+** with required packages:
   ```bash
   pip install faker
   ```

2. **SQLite3** (usually included with Python)

### Setup

First, make all scripts executable:

```bash
cd /Users/manu/Downloads/manuai/bin
chmod +x *.py
```

### Quick Start

Run all database generation scripts at once:

```bash
python generate_all_databases.py
```

### Manual Execution

You can also run individual scripts in order:

#### For 500-table database:
```bash
python generate_arcops_database_500.py
python generate_arcops_database_500_part2.py
python generate_arcops_database_500_part3.py
python generate_arcops_data_500.py
```

#### For 200-table database:
```bash
python generate_arcops_database_200.py
python generate_arcops_database_200_part2.py
python generate_arcops_data_200.py
```

### Alternative Direct Execution

After running `chmod +x *.py`, you can also run scripts directly:

```bash
./generate_all_databases.py
```

However, using `python` explicitly is recommended for better compatibility.

## Database Details

### 500-Table Database Features
- **Comprehensive MES Coverage**: Complete manufacturing execution system
- **Advanced Features**: Document management, training systems, safety management
- **Enterprise Scale**: Designed for large manufacturing operations
- **Full Traceability**: Complete lot/serial number tracking
- **Integration Ready**: External system integration tables

### 200-Table Database Features
- **Core Manufacturing**: Essential manufacturing operations
- **Production Focus**: Work orders, routings, quality control
- **Smaller Scale**: Suitable for mid-size manufacturing operations
- **Complete Workflows**: End-to-end manufacturing processes

### Common Tables in Both Databases

#### Organization Structure
- Companies, Plants, Departments, Work Centers
- Employees, Skills, Shifts

#### Product Management
- Items, Products, Bills of Materials (BOMs)
- Routings, Operations

#### Customer & Supplier Management
- Customers, Suppliers, Contacts
- Sales Orders, Purchase Orders

#### Inventory Management
- Warehouses, Locations, Inventory
- Inventory Transactions

#### Production Execution
- Work Orders, Jobs, Material Allocations
- Production Planning, MRP

#### Quality Control
- Quality Plans, Inspections, Non-conformances
- Quality Characteristics, Test Results

#### Equipment & Maintenance
- Equipment, Maintenance Plans, Maintenance Orders

#### Cost Tracking
- Cost Centers, Labor/Material/Machine Costs

### Sample Data Generated

- **Employees**: 200-500 employees with skills and certifications
- **Customers**: 50-100 customers with contacts
- **Suppliers**: 50-75 suppliers with contacts
- **Items**: 500-1000+ items (raw materials, components, finished goods)
- **Products**: 25-50 products with BOMs and routings
- **Work Orders**: Production orders with operations and jobs
- **Inventory**: Realistic inventory levels and transactions
- **Quality Data**: Inspections, test results, non-conformances

## Database Schema

### Key Relationships
- **Hierarchical Organization**: Companies → Plants → Departments → Work Centers
- **Product Structure**: Products → BOMs → Items
- **Production Flow**: Sales Orders → Work Orders → Jobs → Transactions
- **Quality Integration**: Products → Quality Plans → Inspections → Results
- **Traceability**: Lots → Serial Numbers → Genealogy

### Data Integrity
- Foreign key constraints enabled
- Referential integrity maintained
- Realistic data relationships

## Output

The scripts generate SQLite database files in the `../data/` directory:
- `arcops_manufacturing_500.db` - 500-table database
- `arcops_manufacturing_200.db` - 200-table database

## Connecting to Databases

### SQLite Command Line
```bash
sqlite3 ../data/arcops_manufacturing_500.db
```

### Python
```python
import sqlite3
conn = sqlite3.connect('../data/arcops_manufacturing_500.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM work_orders")
print(cursor.fetchone())
conn.close()
```

### Database Browser
Use any SQLite browser tool like:
- DB Browser for SQLite
- SQLiteStudio
- DBeaver

## Example Queries

### Get all active work orders with product information
```sql
SELECT wo.work_order_number, p.product_name, wo.quantity_ordered, wo.status
FROM work_orders wo
JOIN products p ON wo.product_id = p.id
WHERE wo.status = 'Active'
ORDER BY wo.created_at DESC;
```

### Get employee skills summary
```sql
SELECT e.first_name, e.last_name, s.skill_name, es.proficiency_level
FROM employees e
JOIN employee_skills es ON e.id = es.employee_id
JOIN skills s ON es.skill_id = s.id
WHERE es.is_active = 1
ORDER BY e.last_name, e.first_name;
```

### Get inventory summary by location
```sql
SELECT l.location_code, i.quantity_on_hand, im.item_name
FROM inventory i
JOIN locations l ON i.location_id = l.id
JOIN item_masters im ON i.item_id = im.id
WHERE i.quantity_on_hand > 0
ORDER BY l.location_code;
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure you have write permissions to the data directory
2. **Module Not Found**: Install required packages with `pip install faker`
3. **Database Locked**: Close any existing database connections
4. **Memory Issues**: The 500-table database requires significant memory

### Performance Tips

- Run scripts on systems with adequate RAM (4GB+ recommended)
- Use SSD storage for better performance
- Close other applications during generation

## Customization

### Modifying Data Volume
Edit the range values in data generation scripts:
```python
# Change this:
for i in range(200):  # 200 employees
# To this:
for i in range(500):  # 500 employees
```

### Adding Custom Tables
1. Add table creation SQL to the appropriate database script
2. Add data population logic to the corresponding data script
3. Update foreign key relationships as needed

### Changing Data Patterns
Modify the Faker patterns and random choices in the data scripts to match your specific requirements.

## License

These scripts are provided as-is for educational and development purposes.

## Support

For issues or questions, please check the script output for error messages and ensure all prerequisites are met.

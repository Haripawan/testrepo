import sqlglot
from sqlglot import exp
import json
import os

def extract_sql_details(sql_expression):
    # ... (same function as before)

def create_lineage(sql_details, target_table):
    lineage = {"nodes": [], "edges": []}
    
    # Add tables as nodes
    for table in sql_details["tables"]:
        lineage["nodes"].append({"id": table, "label": table})
    
    # Add columns as nodes and create edges from table to column
    for column in sql_details["columns"]:
        table_name, column_name = column.split('.')
        lineage["nodes"].append({"id": column, "label": column_name})
        lineage["edges"].append({"from": table_name, "to": column})
    
    # Add edges for JOIN logic
    for join in sql_details["join_logic"]:
        join_parts = join.split(' ')
        source_table = join_parts[-1].split('.')[0]
        target_table = join_parts[-3].split('.')[0]
        lineage["edges"].append({"from": source_table, "to": target_table, "label": join})
    
    return lineage

# Read SQL from file named after the target table
target_table = 'target_table_name'  # Replace with your target table name
sql_file_path = f"{target_table}.sql"

if os.path.exists(sql_file_path):
    with open(sql_file_path, 'r') as file:
        sql_query = file.read()
        parsed_sql = sqlglot.parse_one(sql_query)
        sql_details = extract_sql_details(parsed_sql)
        lineage = create_lineage(sql_details, target_table)
        
        # Convert the lineage to JSON
        lineage_json = json.dumps(lineage, indent=4)
        print(lineage_json)
else:
    print(f"No SQL file found for the target table: {target_table}")

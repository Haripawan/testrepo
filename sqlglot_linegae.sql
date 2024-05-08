from sqlglot import parse_one, exp
from sqlglot.generator import generate
from sqlglot.optimizer.scope import Scope

def extract_lineage(sql):
    # Parse the SQL query into an expression tree
    expression = parse_one(sql)

    # Generate the scope which contains the lineage information
    scope = Scope(expression)

    # Traverse the expression tree to extract lineage information
    lineage_info = []
    for column in scope.columns.values():
        lineage_info.append({
            'column': column.name,
            'lineage': [parent.name for parent in column.parents]
        })

    return lineage_info

# Example SQL query with complex transformations and joins
complex_oracle_sql = """
SELECT
    a.column1 + b.column2 AS result_column,
    c.column3
FROM
    table1 a
JOIN
    table2 b ON a.id = b.id
JOIN
    (SELECT id, column3 FROM table3) c ON a.id = c.id
"""

# Extract lineage from the complex Oracle SQL query
lineage = extract_lineage(complex_oracle_sql)

# Output the lineage information
for line in lineage:
    print(f"Column: {line['column']}")
    print(f"Lineage: {', '.join(line['lineage'])}")
    print()

##############

from sqlglot import parse_one
from sqlglot.expressions import Column

def extract_lineage(sql):
    # Parse the SQL query into an expression tree
    expression = parse_one(sql)

    # Traverse the expression tree to extract lineage information
    lineage_info = []
    for exp in expression.find_all(Column):
        lineage_info.append({
            'column': exp.sql(),
            'lineage': [parent.sql() for parent in exp.find_ancestors(Column)]
        })

    return lineage_info

# Example usage with a complex SQL query
complex_sql = "SELECT a.col1, b.col2 FROM table_a a JOIN table_b b ON a.id = b.id"
lineage = extract_lineage(complex_sql)

# Output the lineage information
for line in lineage:
    print(f"Column: {line['column']}")
    print(f"Lineage: {', '.join(line['lineage'])}")


###### version3#######

from sqlglot import parse_one
from sqlglot.optimizer import Scope

def generate_lineage(sql):
    # Parse the SQL query into an expression tree
    expression = parse_one(sql)

    # Generate the scope which contains the lineage information
    scope = Scope(expression)

    # Traverse the expression tree to extract lineage information
    lineage_info = []
    for column in scope.columns.values():
        # Extract the table name and column name
        table_name = column.table
        column_name = column.name

        # Find the source columns for the current column
        source_columns = [
            f"{parent.table}.{parent.name}" for parent in column.parents
        ] if column.parents else []

        lineage_info.append({
            'column': f"{table_name}.{column_name}",
            'lineage': source_columns
        })

    return lineage_info

# Example SQL query with complex transformations and joins
complex_sql = """
SELECT
    a.col1 AS transformed_col1,
    b.col2,
    c.col3
FROM
    table1 a
JOIN
    table2 b ON a.id = b.id
JOIN
    (SELECT id, col3 FROM table3) c ON a.id = c.id
"""

# Generate lineage from the complex SQL query
lineage = generate_lineage(complex_sql)

# Output the lineage information
for line in lineage:
    print(f"Column: {line['column']}")
    print(f"Lineage: {', '.join(line['lineage'])}")

#######version 4########


To extract the lineage information from the Oracle SQL query and output it as JSON, you can modify the Python code to generate a JSON object containing the tables and columns involved. Here's how you can do it:

```python
import json
from sqlglot import parse

def extract_tables_and_columns(node):
    tables = []
    columns = []
    if node.type == 'Identifier':
        if node.is_child_of('From'):
            tables.append(node.get_source())
        elif node.is_child_of('Select'):
            columns.append(node.value)
    for child in node.children:
        child_tables, child_columns = extract_tables_and_columns(child)
        tables.extend(child_tables)
        columns.extend(child_columns)
    return tables, columns

def trace_data_lineage(sql_query):
    parsed_query = parse(sql_query, flavor='oracle')
    tables, columns = extract_tables_and_columns(parsed_query)
    return {"tables": tables, "columns": columns}

# Example Oracle SQL query with dynamic joins and inner queries
oracle_query = """
SELECT t1.col1, t2.col2
FROM table1 t1
JOIN table2 t2 ON t1.id = t2.id
WHERE t1.col3 IN (SELECT col FROM table3 WHERE condition)
"""

# Trace data lineage
lineage_json = trace_data_lineage(oracle_query)

# Output lineage as JSON
print(json.dumps(lineage_json, indent=4))
```

This code will output the lineage information extracted from the Oracle SQL query as a JSON object. The JSON object will have two keys: "tables" containing a list of tables involved and "columns" containing a list of columns selected in the query. You can further extend this code to include additional information or structure the JSON output according to your requirements.


######version5 ######

from graphviz import Digraph
from sqlglot import parse_one
from sqlglot.expressions import Column

def extract_lineage_with_table(sql):
    # Parse the SQL query into an expression tree
    expression = parse_one(sql)

    # Traverse the expression tree to extract lineage information
    lineage_info = []
    for exp in expression.find_all(Column):
        # Include the table name with the column name
        full_column_name = f"{exp.table}.{exp.name}" if exp.table else exp.name
        lineage_info.append({
            'column': full_column_name,
            'lineage': [
                f"{ancestor.table}.{ancestor.name}" if ancestor.table else ancestor.name
                for ancestor in exp.find_ancestors(Column)
            ]
        })

    return lineage_info

def visualize_lineage(lineage_info):
    dot = Digraph(comment='Column Lineage')

    for line in lineage_info:
        # Create nodes for the column
        dot.node(line['column'], line['column'])

        # Create edges from source columns to the target column
        for ancestor in line['lineage']:
            dot.edge(ancestor, line['column'])

    return dot

# Example usage with a complex SQL query
complex_sql = "SELECT a.col1, b.col2 FROM table_a a JOIN table_b b ON a.id = b.id"
lineage = extract_lineage_with_table(complex_sql)

# Generate the visualization
dot = visualize_lineage(lineage)

# Render the visualization to a file (e.g., PDF, PNG)
dot.render('lineage_graph', view=True)



### version 6####

from sqlglot import parse_one
from sqlglot.expressions import Column, Table

def extract_lineage_with_actual_table_names(sql):
    # Parse the SQL query into an expression tree
    expression = parse_one(sql)

    # Create a mapping of aliases to actual table names
    alias_to_table = {
        alias.alias: alias.this
        for alias in expression.find_all(Table)
        if alias.alias
    }

    # Traverse the expression tree to extract lineage information
    lineage_info = []
    for exp in expression.find_all(Column):
        # Replace alias with actual table name if it exists
        table_name = alias_to_table.get(exp.table, exp.table)
        full_column_name = f"{table_name}.{exp.name}" if table_name else exp.name

        # Find the source columns for the current column
        source_columns = [
            f"{alias_to_table.get(parent.table, parent.table)}.{parent.name}"
            if parent.table else parent.name
            for parent in exp.find_ancestors(Column)
        ] if exp.find_ancestors(Column) else []

        lineage_info.append({
            'column': full_column_name,
            'lineage': source_columns
        })

    return lineage_info

# Example usage with a complex SQL query
complex_sql = """
SELECT a.col1, b.col2
FROM table_a AS a
JOIN table_b AS b ON a.id = b.id
"""
lineage = extract_lineage_with_actual_table_names(complex_sql)

# Output the lineage information
for line in lineage:
    print(f"Column: {line['column']}")
    print(f"Lineage: {', '.join(line['lineage'])}")

##### version 7####

from sqlglot import parse_one
from sqlglot.expressions import Alias, Column

def extract_lineage_with_table_aliases(sql):
    # Parse the SQL query into an expression tree
    expression = parse_one(sql)

    # Create a mapping of aliases to actual table names
    alias_to_table = {
        alias.alias: alias.this.name
        for alias in expression.find_all(Alias)
    }

    # Traverse the expression tree to extract lineage information
    lineage_info = []
    for exp in expression.find_all(Column):
        # If the column has an alias and no table, use the alias as the table name
        table_name = alias_to_table.get(exp.table, exp.alias or exp.table)
        full_column_name = f"{table_name}.{exp.name}" if table_name else exp.name

        # Find the source columns for the current column
        source_columns = [
            f"{alias_to_table.get(parent.table, parent.alias or parent.table)}.{parent.name}"
            if parent.table or parent.alias else parent.name
            for parent in exp.find_ancestors(Column)
        ] if exp.find_ancestors(Column) else []

        lineage_info.append({
            'column': full_column_name,
            'lineage': source_columns
        })

    return lineage_info

# Example usage with a complex SQL query
complex_sql = """
SELECT a.col1, SUM(b.amount) AS total_amount
FROM table_a AS a
JOIN table_b AS b ON a.id = b.id
GROUP BY a.col1
"""
lineage = extract_lineage_with_table_aliases(complex_sql)

# Output the lineage information
for line in lineage:
    print(f"Column: {line['column']}")
    print(f"Lineage: {', '.join(line['lineage'])}")


####version 8####

from sqlglot import parse

def extract_data_lineage(sql_query):
    parsed_query = parse(sql_query)
    lineage = []

    for node in parsed_query:
        if node['type'] == 'select':
            # Extract columns from the SELECT statement
            for item in node['value']:
                if item['type'] == 'column':
                    lineage.append(('source', item['name']))
        elif node['type'] == 'join':
            # Extract columns involved in JOIN conditions
            for condition in node['on']:
                if condition['type'] == 'condition':
                    if condition['left']['type'] == 'column':
                        lineage.append(('source', condition['left']['name']))
                    if condition['right']['type'] == 'column':
                        lineage.append(('source', condition['right']['name']))
        elif node['type'] == 'from':
            # Extract tables and columns from the FROM clause
            for item in node['value']:
                if item['type'] == 'table':
                    lineage.append(('destination', item['name']))
                elif item['type'] == 'column':
                    lineage.append(('destination', item['name']))

    return lineage

# Sample SQL query
sql_query = """
SELECT a.column1, b.column2
FROM table_a a
JOIN table_b b ON a.id = b.id
"""

# Extract data lineage
data_lineage = extract_data_lineage(sql_query)
print(data_lineage)

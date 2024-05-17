import sqlglot
import pandas as pd

# Example SQL query
sql = """
SELECT a.id, b.name, COUNT(*) as count, SUM(c.amount) as total_amount
FROM table_a a
JOIN table_b b ON a.id = b.a_id
JOIN table_c c ON a.id = c.a_id
WHERE a.date > '2021-01-01'
GROUP BY a.id, b.name
ORDER BY total_amount DESC;
"""

# Parse the SQL query
parsed = sqlglot.parse_one(sql)

# Extract columns
def extract_columns(parsed_query):
    columns = [str(col) for col in parsed_query.find_all(sqlglot.expressions.Column)]
    return columns

# Extract column transformations
def extract_transformations(parsed_query):
    transformations = {str(alias.alias): str(alias.this) for alias in parsed_query.find_all(sqlglot.expressions.Alias)}
    return transformations

# Extract tables
def extract_tables(parsed_query):
    tables = [str(table) for table in parsed_query.find_all(sqlglot.expressions.Table)]
    return tables

# Extract column dependencies
def extract_dependencies(parsed_query):
    dependencies = {}
    
    # Helper function to populate dependencies
    def populate_dependencies(expression, alias=None):
        if isinstance(expression, sqlglot.expressions.Column):
            table = expression.table
            column = expression.name
            key = f"{table}.{column}" if table else column
            if alias:
                dependencies[alias] = key
            else:
                dependencies[column] = key
        elif isinstance(expression, sqlglot.expressions.Alias):
            populate_dependencies(expression.this, alias=str(expression.alias))
    
    for expr in parsed_query.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias)):
        populate_dependencies(expr)
    
    return dependencies

# Extract information
columns = extract_columns(parsed)
transformations = extract_transformations(parsed)
tables = extract_tables(parsed)
dependencies = extract_dependencies(parsed)

# Prepare DataFrame data
data = []

for col in columns:
    col_name = col.split('.')[-1]
    table_name = col.split('.')[0] if '.' in col else None
    transformation = transformations.get(col_name, None)
    dependency = dependencies.get(col_name, col)
    
    data.append({
        "Column": col_name,
        "Transformation": transformation,
        "Table": table_name,
        "Dependency": dependency
    })

# Create DataFrame
df = pd.DataFrame(data)

# Print DataFrame
print(df)
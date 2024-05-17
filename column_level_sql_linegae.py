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
    return [col for col in parsed_query.find_all(sqlglot.expressions.Column)]

# Extract column transformations
def extract_transformations(parsed_query):
    transformations = {}
    for alias in parsed_query.find_all(sqlglot.expressions.Alias):
        if isinstance(alias.this, sqlglot.expressions.Func):
            transformations[alias.alias] = alias.this.sql()
        else:
            transformations[alias.alias] = str(alias.this)
    return transformations

# Extract table aliases and their actual names
def extract_table_aliases(parsed_query):
    table_aliases = {}
    for table in parsed_query.find_all(sqlglot.expressions.Table):
        if table.alias:
            table_aliases[table.alias] = table.this
        else:
            table_aliases[str(table.this)] = table.this
    return table_aliases

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
table_aliases = extract_table_aliases(parsed)
dependencies = extract_dependencies(parsed)

# Prepare DataFrame data
data = []

for col in columns:
    col_name = col.name
    table_alias = col.table
    table_name = table_aliases.get(table_alias, table_alias)
    transformation = transformations.get(col_name, None)
    dependency = dependencies.get(col_name, f"{table_name}.{col_name}" if table_name else col_name)
    
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
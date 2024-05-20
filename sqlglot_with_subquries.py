import sqlglot
import pandas as pd

# Example SQL query with a subquery
sql = """
SELECT main.id, subquery.total_amount, main.name
FROM (
    SELECT a.id, SUM(c.amount) as total_amount
    FROM table_a a
    JOIN table_c c ON a.id = c.a_id
    GROUP BY a.id
) subquery
JOIN table_b main ON subquery.id = main.id
WHERE main.date > '2021-01-01'
ORDER BY subquery.total_amount DESC;
"""

# Parse the SQL query
parsed = sqlglot.parse_one(sql)

def extract_elements(parsed_query):
    columns = []
    transformations = {}
    table_aliases = {}
    dependencies = {}

    queue = [parsed_query]
    
    while queue:
        current = queue.pop(0)
        
        for col in current.find_all(sqlglot.expressions.Column):
            columns.append(col)
        
        for alias in current.find_all(sqlglot.expressions.Alias):
            columns.append(alias)
            transformations[str(alias.alias)] = alias.this.sql()
        
        for table in current.find_all(sqlglot.expressions.Table):
            if table.alias:
                table_aliases[str(table.alias)] = str(table.this)
            else:
                table_aliases[str(table.this)] = str(table.this)
        
        for subquery in current.find_all(sqlglot.expressions.Subquery):
            queue.append(subquery)
        
        def populate_dependencies(expression, alias=None):
            if isinstance(expression, sqlglot.expressions.Column):
                table = expression.table
                column = expression.name
                key = f"{table}.{column}" if table else column
                if alias:
                    if alias not in dependencies:
                        dependencies[alias] = []
                    dependencies[alias].append(key)
                else:
                    if column not in dependencies:
                        dependencies[column] = []
                    dependencies[column].append(key)
            elif isinstance(expression, sqlglot.expressions.Alias):
                populate_dependencies(expression.this, alias=str(expression.alias))
            elif isinstance(expression, sqlglot.expressions.Func):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)

        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias, sqlglot.expressions.Func)):
            populate_dependencies(expr)
    
    return columns, transformations, table_aliases, dependencies

# Extract information
columns, transformations, table_aliases, dependencies = extract_elements(parsed)

# Prepare DataFrame data
data = []

for col in columns:
    if isinstance(col, sqlglot.expressions.Column):
        col_name = col.name
        table_alias = col.table
    elif isinstance(col, sqlglot.expressions.Alias):
        col_name = col.alias
        table_alias = col.this.table if hasattr(col.this, 'table') else None
    
    table_name = table_aliases.get(table_alias, table_alias)
    transformation = transformations.get(col_name, None)
    dependency = dependencies.get(col_name, [f"{table_name}.{col_name}" if table_name else col_name])
    
    data.append({
        "Column": col_name,
        "Transformation": transformation,
        "Table": table_name,
        "Dependencies": ', '.join(dependency)
    })

# Create DataFrame
df = pd.DataFrame(data)

# Print DataFrame
print(df)
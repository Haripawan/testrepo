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


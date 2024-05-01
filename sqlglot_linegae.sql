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

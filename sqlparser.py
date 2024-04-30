import sqlglot
from sqlglot import exp
import json

def extract_from_expression(expression):
    if isinstance(expression, exp.Table):
        return [expression.name]
    elif isinstance(expression, exp.Subquery):
        return extract_sql_details(expression.this)
    return []

def extract_sql_details(sql_expression):
    tables = []
    columns = []
    column_logic = []
    where_conditions = []
    join_logic = []
    
    for table_exp in sql_expression.find_all(exp.Table, exp.Subquery):
        tables.extend(extract_from_expression(table_exp))
    
    for column in sql_expression.find_all(exp.Column):
        table_name = column.table or 'UNKNOWN_TABLE'
        column_name = column.name
        columns.append(f"{table_name}.{column_name}")
    
    column_logic = [str(projection) for select in sql_expression.find_all(exp.Select)
                    for projection in select.expressions]
    
    where_conditions = [str(where) for where in sql_expression.find_all(exp.Where)]
    
    for join in sql_expression.find_all(exp.Join):
        join_type = join.args.get('kind')
        join_condition = str(join.args.get('on'))
        join_logic.append(f"{join_type} JOIN ON {join_condition}")
    
    # Create a dictionary to store all the extracted information
    sql_details = {
        "tables": tables,
        "columns": columns,
        "column_logic": column_logic,
        "where_conditions": where_conditions,
        "join_logic": join_logic
    }
    
    return sql_details

# Example usage
sql_query = """
SELECT d.a, (SELECT e.b FROM e) AS sub_b FROM d
LEFT JOIN f ON d.id = f.d_id
WHERE d.a > 10 AND d.id IS NOT NULL
"""
parsed_sql = sqlglot.parse_one(sql_query)
sql_details = extract_sql_details(parsed_sql)

# Convert the details to JSON
sql_details_json = json.dumps(sql_details, indent=4)
print(sql_details_json)

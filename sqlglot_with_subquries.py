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

    stack = [parsed_query]
    
    while stack:
        current = stack.pop()
        
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
            stack.append(subquery)
        
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



#### optimised code ######

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
    
    stack = [parsed_query]

    while stack:
        current = stack.pop()
        
        # Extract columns and aliases
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias)):
            if isinstance(expr, sqlglot.expressions.Column):
                columns.append(expr)
            elif isinstance(expr, sqlglot.expressions.Alias):
                columns.append(expr)
                transformations[str(expr.alias)] = expr.this.sql()

        # Extract tables and their aliases
        for table in current.find_all(sqlglot.expressions.Table):
            if table.alias:
                table_aliases[str(table.alias)] = str(table.this)
            else:
                table_aliases[str(table.this)] = str(table.this)
        
        # Process subqueries iteratively
        for subquery in current.find_all(sqlglot.expressions.Subquery):
            stack.append(subquery)
        
        # Extract dependencies
        def populate_dependencies(expression, alias=None):
            if isinstance(expression, sqlglot.expressions.Column):
                table = expression.table
                column = expression.name
                key = f"{table}.{column}" if table else column
                if alias:
                    dependencies.setdefault(alias, []).append(key)
                else:
                    dependencies.setdefault(column, []).append(key)
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



###### with window functions#####

import sqlglot
import pandas as pd

# Example SQL query with functions
sql = """
SELECT 
    main.id, 
    subquery.total_amount, 
    main.name, 
    ROW_NUMBER() OVER (PARTITION BY main.name ORDER BY main.date) as row_num,
    GREATEST(main.score, 0) as max_score,
    COALESCE(main.description, 'N/A') as description
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

    stack = [parsed_query]

    while stack:
        current = stack.pop()
        
        # Extract columns and aliases
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias)):
            if isinstance(expr, sqlglot.expressions.Column):
                columns.append(expr)
            elif isinstance(expr, sqlglot.expressions.Alias):
                columns.append(expr)
                transformations[str(expr.alias)] = expr.this.sql()

        # Extract tables and their aliases
        for table in current.find_all(sqlglot.expressions.Table):
            if table.alias:
                table_aliases[str(table.alias)] = str(table.this)
            else:
                table_aliases[str(table.this)] = str(table.this)
        
        # Process subqueries iteratively
        for subquery in current.find_all(sqlglot.expressions.Subquery):
            stack.append(subquery)
        
        # Extract dependencies
        def populate_dependencies(expression, alias=None):
            if isinstance(expression, sqlglot.expressions.Column):
                table = expression.table
                column = expression.name
                key = f"{table}.{column}" if table else column
                if alias:
                    dependencies.setdefault(alias, []).append(key)
                else:
                    dependencies.setdefault(column, []).append(key)
            elif isinstance(expression, sqlglot.expressions.Alias):
                populate_dependencies(expression.this, alias=str(expression.alias))
            elif isinstance(expression, sqlglot.expressions.Func):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
            elif isinstance(expression, sqlglot.expressions.Window):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
        
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias, sqlglot.expressions.Func, sqlglot.expressions.Window)):
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

######## join and filters #######

import sqlglot
import pandas as pd

# Example SQL query with functions, join logic, and filter condition
sql = """
SELECT 
    main.id, 
    subquery.total_amount, 
    main.name, 
    ROW_NUMBER() OVER (PARTITION BY main.name ORDER BY main.date) as row_num,
    GREATEST(main.score, 0) as max_score,
    COALESCE(main.description, 'N/A') as description
FROM (
    SELECT a.id, SUM(c.amount) as total_amount
    FROM table_a a
    JOIN table_c c ON a.id = c.a_id
    GROUP BY a.id
) subquery
JOIN table_b main ON subquery.id = main.id
LEFT JOIN table_d d ON main.id = d.b_id
WHERE main.date > '2021-01-01' AND d.some_column = 'some_value'
ORDER BY subquery.total_amount DESC;
"""

# Parse the SQL query
parsed = sqlglot.parse_one(sql)

def extract_elements(parsed_query):
    columns = []
    transformations = {}
    table_aliases = {}
    dependencies = {}
    joins = []
    filters = []

    stack = [parsed_query]

    while stack:
        current = stack.pop()
        
        # Extract columns and aliases
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias)):
            if isinstance(expr, sqlglot.expressions.Column):
                columns.append(expr)
            elif isinstance(expr, sqlglot.expressions.Alias):
                columns.append(expr)
                transformations[str(expr.alias)] = expr.this.sql()

        # Extract tables and their aliases
        for table in current.find_all(sqlglot.expressions.Table):
            if table.alias:
                table_aliases[str(table.alias)] = str(table.this)
            else:
                table_aliases[str(table.this)] = str(table.this)
        
        # Process subqueries iteratively
        for subquery in current.find_all(sqlglot.expressions.Subquery):
            stack.append(subquery)
        
        # Extract joins
        for join in current.find_all(sqlglot.expressions.Join):
            joins.append(join)
        
        # Extract filters
        for where in current.find_all(sqlglot.expressions.Where):
            filters.append(where)
        
        # Extract dependencies
        def populate_dependencies(expression, alias=None):
            if isinstance(expression, sqlglot.expressions.Column):
                table = expression.table
                column = expression.name
                key = f"{table}.{column}" if table else column
                if alias:
                    dependencies.setdefault(alias, []).append(key)
                else:
                    dependencies.setdefault(column, []).append(key)
            elif isinstance(expression, sqlglot.expressions.Alias):
                populate_dependencies(expression.this, alias=str(expression.alias))
            elif isinstance(expression, sqlglot.expressions.Func):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
            elif isinstance(expression, sqlglot.expressions.Window):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
        
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias, sqlglot.expressions.Func, sqlglot.expressions.Window)):
            populate_dependencies(expr)
    
    return columns, transformations, table_aliases, dependencies, joins, filters

# Extract information
columns, transformations, table_aliases, dependencies, joins, filters = extract_elements(parsed)

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
    
    # Fetch dependencies for the alias or column
    dependency_list = dependencies.get(col_name, [])
    
    for dependency in dependency_list:
        source_table, source_column = dependency.split('.') if '.' in dependency else (None, dependency)
        data.append({
            "Column": col_name,
            "Column_Transformation": transformation,
            "Source_Table": source_table,
            "Source_Column": source_column
        })

# Prepare DataFrame for joins
join_data = []

for join in joins:
    if hasattr(join, 'left'):
        left_table = table_aliases.get(str(join.left), None)
    else:
        left_table = None

    if hasattr(join, 'right'):
        right_table = table_aliases.get(str(join.right), None)
    else:
        right_table = None

    if hasattr(join, 'on_this'):
        on_condition = join.on_this.sql()
    else:
        on_condition = None

    join_data.append({
        "Join_Type": join.kind.upper(),
        "Left_Table": left_table,
        "Right_Table": right_table,
        "On_Condition": on_condition
    })

# Prepare DataFrame for filters
filter_data = []

for where in filters:
    filter_data.append({
        "Filter_Condition": where.this.sql()
    })

# Create DataFrames
df = pd.DataFrame(data)
join_df = pd.DataFrame(join_data)
filter_df = pd.DataFrame(filter_data)

# Print DataFrames
print("Columns Information:")
print(df)
print("\nJoins Information:")
print(join_df)
print("\nFilters Information:")
print(filter_df)


################## extraction joins from subquries ##########

import sqlglot
import pandas as pd

# Example SQL query with functions, join logic, and filter condition
sql = """
SELECT 
    main.id, 
    subquery.total_amount, 
    main.name, 
    ROW_NUMBER() OVER (PARTITION BY main.name ORDER BY main.date) as row_num,
    GREATEST(main.score, 0) as max_score,
    COALESCE(main.description, 'N/A') as description
FROM (
    SELECT a.id, SUM(c.amount) as total_amount
    FROM table_a a
    JOIN table_c c ON a.id = c.a_id
    GROUP BY a.id
) subquery
JOIN table_b main ON subquery.id = main.id
LEFT JOIN table_d d ON main.id = d.b_id
WHERE main.date > '2021-01-01' AND d.some_column = 'some_value'
ORDER BY subquery.total_amount DESC;
"""

# Parse the SQL query
parsed = sqlglot.parse_one(sql)

def extract_elements(parsed_query):
    columns = []
    transformations = {}
    table_aliases = {}
    dependencies = {}
    joins = []
    filters = []

    stack = [parsed_query]

    while stack:
        current = stack.pop()
        
        # Extract columns and aliases
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias)):
            if isinstance(expr, sqlglot.expressions.Column):
                columns.append(expr)
            elif isinstance(expr, sqlglot.expressions.Alias):
                columns.append(expr)
                transformations[str(expr.alias)] = expr.this.sql()

        # Extract tables and their aliases
        for table in current.find_all(sqlglot.expressions.Table):
            if table.alias:
                table_aliases[str(table.alias)] = str(table.this)
            else:
                table_aliases[str(table.this)] = str(table.this)
        
        # Process subqueries iteratively
        for subquery in current.find_all(sqlglot.expressions.Subquery):
            stack.append(subquery)
            sub_columns, sub_transformations, sub_table_aliases, sub_dependencies, sub_joins, sub_filters = extract_elements(subquery)
            columns.extend(sub_columns)
            transformations.update(sub_transformations)
            table_aliases.update(sub_table_aliases)
            dependencies.update(sub_dependencies)
            joins.extend(sub_joins)
            filters.extend(sub_filters)
        
        # Extract joins
        for join in current.find_all(sqlglot.expressions.Join):
            joins.append(join)
        
        # Extract filters
        for where in current.find_all(sqlglot.expressions.Where):
            filters.append(where)
        
        # Extract dependencies
        def populate_dependencies(expression, alias=None):
            if isinstance(expression, sqlglot.expressions.Column):
                table = expression.table
                column = expression.name
                key = f"{table}.{column}" if table else column
                if alias:
                    dependencies.setdefault(alias, []).append(key)
                else:
                    dependencies.setdefault(column, []).append(key)
            elif isinstance(expression, sqlglot.expressions.Alias):
                populate_dependencies(expression.this, alias=str(expression.alias))
            elif isinstance(expression, sqlglot.expressions.Func):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
            elif isinstance(expression, sqlglot.expressions.Window):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
        
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias, sqlglot.expressions.Func, sqlglot.expressions.Window)):
            populate_dependencies(expr)
    
    return columns, transformations, table_aliases, dependencies, joins, filters

# Extract information
columns, transformations, table_aliases, dependencies, joins, filters = extract_elements(parsed)

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
    
    # Fetch dependencies for the alias or column
    dependency_list = dependencies.get(col_name, [])
    
    for dependency in dependency_list:
        source_table, source_column = dependency.split('.') if '.' in dependency else (None, dependency)
        data.append({
            "Column": col_name,
            "Column_Transformation": transformation,
            "Source_Table": source_table,
            "Source_Column": source_column
        })

# Prepare DataFrame for joins
join_data = []

for join in joins:
    if hasattr(join, 'left'):
        left_table = table_aliases.get(str(join.left), None)
    else:
        left_table = None

    if hasattr(join, 'right'):
        right_table = table_aliases.get(str(join.right), None)
    else:
        right_table = None

    if hasattr(join, 'on_this'):
        on_condition = join.on_this.sql()
    else:
        on_condition = None

    join_data.append({
        "Join_Type": join.kind.upper(),
        "Left_Table": left_table,
        "Right_Table": right_table,
        "On_Condition": on_condition
    })

# Prepare DataFrame for filters
filter_data = []

for where in filters:
    filter_data.append({
        "Filter_Condition": where.this.sql()
    })

# Create DataFrames
df = pd.DataFrame(data)
join_df = pd.DataFrame(join_data)
filter_df = pd.DataFrame(filter_data)

# Print DataFrames
print("Columns Information:")
print(df)
print("\nJoins Information:")
print(join_df)
print("\nFilters Information:")
print(filter_df)


#####proper join conditions #######

import sqlglot
import pandas as pd

# Example SQL query with functions, join logic, and filter condition
sql = """
SELECT 
    main.id, 
    subquery.total_amount, 
    main.name, 
    ROW_NUMBER() OVER (PARTITION BY main.name ORDER BY main.date) as row_num,
    GREATEST(main.score, 0) as max_score,
    COALESCE(main.description, 'N/A') as description
FROM (
    SELECT a.id, SUM(c.amount) as total_amount
    FROM table_a a
    JOIN table_c c ON a.id = c.a_id
    GROUP BY a.id
) subquery
JOIN table_b main ON subquery.id = main.id
LEFT JOIN table_d d ON main.id = d.b_id
WHERE main.date > '2021-01-01' AND d.some_column = 'some_value'
ORDER BY subquery.total_amount DESC;
"""

# Parse the SQL query
parsed = sqlglot.parse_one(sql)

def extract_elements(parsed_query):
    columns = []
    transformations = {}
    table_aliases = {}
    dependencies = {}
    joins = []
    filters = []

    stack = [parsed_query]

    while stack:
        current = stack.pop()
        
        # Extract columns and aliases
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias)):
            if isinstance(expr, sqlglot.expressions.Column):
                columns.append(expr)
            elif isinstance(expr, sqlglot.expressions.Alias):
                columns.append(expr)
                transformations[str(expr.alias)] = expr.this.sql()

        # Extract tables and their aliases
        for table in current.find_all(sqlglot.expressions.Table):
            if table.alias:
                table_aliases[str(table.alias)] = str(table.this)
            else:
                table_aliases[str(table.this)] = str(table.this)
        
        # Process subqueries iteratively
        for subquery in current.find_all(sqlglot.expressions.Subquery):
            stack.append(subquery)
            sub_columns, sub_transformations, sub_table_aliases, sub_dependencies, sub_joins, sub_filters = extract_elements(subquery)
            columns.extend(sub_columns)
            transformations.update(sub_transformations)
            table_aliases.update(sub_table_aliases)
            dependencies.update(sub_dependencies)
            joins.extend(sub_joins)
            filters.extend(sub_filters)
        
        # Extract joins
        for join in current.find_all(sqlglot.expressions.Join):
            join_type = join.args.get("kind", None)
            left_table = join.args.get("this", None)
            right_table = join.args.get("expression", None)
            on_condition = join.args.get("on", None)
            joins.append({
                "Join_Type": join_type.sql().upper() if join_type else None,
                "Left_Table": left_table.sql() if left_table else None,
                "Right_Table": right_table.sql() if right_table else None,
                "On_Condition": on_condition.sql() if on_condition else None
            })
        
        # Extract filters
        for where in current.find_all(sqlglot.expressions.Where):
            filters.append(where)
        
        # Extract dependencies
        def populate_dependencies(expression, alias=None):
            if isinstance(expression, sqlglot.expressions.Column):
                table = expression.table
                column = expression.name
                key = f"{table}.{column}" if table else column
                if alias:
                    dependencies.setdefault(alias, []).append(key)
                else:
                    dependencies.setdefault(column, []).append(key)
            elif isinstance(expression, sqlglot.expressions.Alias):
                populate_dependencies(expression.this, alias=str(expression.alias))
            elif isinstance(expression, sqlglot.expressions.Func):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
            elif isinstance(expression, sqlglot.expressions.Window):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
        
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias, sqlglot.expressions.Func, sqlglot.expressions.Window)):
            populate_dependencies(expr)
    
    return columns, transformations, table_aliases, dependencies, joins, filters

# Extract information
columns, transformations, table_aliases, dependencies, joins, filters = extract_elements(parsed)

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
    
    # Fetch dependencies for the alias or column
    dependency_list = dependencies.get(col_name, [])
    
    for dependency in dependency_list:
        source_table, source_column = dependency.split('.') if '.' in dependency else (None, dependency)
        data.append({
            "Column": col_name,
            "Column_Transformation": transformation,
            "Source_Table": source_table,
            "Source_Column": source_column
        })

# Prepare DataFrame for joins
join_data = []

for join in joins:
    join_data.append({
        "Join_Type": join["Join_Type"],
        "Left_Table": join["Left_Table"],
        "Right_Table": join["Right_Table"],
        "On_Condition": join["On_Condition"]
    })

# Prepare DataFrame for filters
filter_data = []

for where in filters:
    filter_data.append({
        "Filter_Condition": where.this.sql()
    })

# Create DataFrames
df = pd.DataFrame(data)
join_df = pd.DataFrame(join_data)
filter_df = pd.DataFrame(filter_data)

# Print DataFrames
print("Columns Information:")
print(df)
print("\nJoins Information:")
print(join_df)
print("\nFilters Information:")
print(filter_df)



#####fixing the joins ########

import sqlglot
import pandas as pd

# Example SQL query with functions, join logic, and filter condition
sql = """
SELECT 
    main.id, 
    subquery.total_amount, 
    main.name, 
    ROW_NUMBER() OVER (PARTITION BY main.name ORDER BY main.date) as row_num,
    GREATEST(main.score, 0) as max_score,
    COALESCE(main.description, 'N/A') as description
FROM (
    SELECT a.id, SUM(c.amount) as total_amount
    FROM table_a a
    JOIN table_c c ON a.id = c.a_id
    GROUP BY a.id
) subquery
JOIN table_b main ON subquery.id = main.id
LEFT JOIN table_d d ON main.id = d.b_id
WHERE main.date > '2021-01-01' AND d.some_column = 'some_value'
ORDER BY subquery.total_amount DESC;
"""

# Parse the SQL query
parsed = sqlglot.parse_one(sql)

def extract_elements(parsed_query):
    columns = []
    transformations = {}
    table_aliases = {}
    dependencies = {}
    joins = []
    filters = []

    stack = [parsed_query]

    while stack:
        current = stack.pop()
        
        # Extract columns and aliases
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias)):
            if isinstance(expr, sqlglot.expressions.Column):
                columns.append(expr)
            elif isinstance(expr, sqlglot.expressions.Alias):
                columns.append(expr)
                transformations[str(expr.alias)] = expr.this.sql()

        # Extract tables and their aliases
        for table in current.find_all(sqlglot.expressions.Table):
            if table.alias:
                table_aliases[str(table.alias)] = str(table.this)
            else:
                table_aliases[str(table.this)] = str(table.this)
        
        # Process subqueries iteratively
        for subquery in current.find_all(sqlglot.expressions.Subquery):
            stack.append(subquery)
            sub_columns, sub_transformations, sub_table_aliases, sub_dependencies, sub_joins, sub_filters = extract_elements(subquery)
            columns.extend(sub_columns)
            transformations.update(sub_transformations)
            table_aliases.update(sub_table_aliases)
            dependencies.update(sub_dependencies)
            joins.extend(sub_joins)
            filters.extend(sub_filters)
        
        # Extract joins
        for join in current.find_all(sqlglot.expressions.Join):
            join_type = join.args.get("kind")
            left_table = join.args.get("this")
            right_table = join.args.get("expression")
            on_condition = join.args.get("on")
            joins.append({
                "Join_Type": join_type.upper() if join_type else None,
                "Left_Table": left_table.sql() if left_table else None,
                "Right_Table": right_table.sql() if right_table else None,
                "On_Condition": on_condition.sql() if on_condition else None
            })
        
        # Extract filters
        for where in current.find_all(sqlglot.expressions.Where):
            filters.append(where)
        
        # Extract dependencies
        def populate_dependencies(expression, alias=None):
            if isinstance(expression, sqlglot.expressions.Column):
                table = expression.table
                column = expression.name
                key = f"{table}.{column}" if table else column
                if alias:
                    dependencies.setdefault(alias, []).append(key)
                else:
                    dependencies.setdefault(column, []).append(key)
            elif isinstance(expression, sqlglot.expressions.Alias):
                populate_dependencies(expression.this, alias=str(expression.alias))
            elif isinstance(expression, sqlglot.expressions.Func):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
            elif isinstance(expression, sqlglot.expressions.Window):
                for arg in expression.args.values():
                    populate_dependencies(arg, alias)
        
        for expr in current.find_all((sqlglot.expressions.Column, sqlglot.expressions.Alias, sqlglot.expressions.Func, sqlglot.expressions.Window)):
            populate_dependencies(expr)
    
    return columns, transformations, table_aliases, dependencies, joins, filters

# Extract information
columns, transformations, table_aliases, dependencies, joins, filters = extract_elements(parsed)

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
    
    # Fetch dependencies for the alias or column
    dependency_list = dependencies.get(col_name, [])
    
    for dependency in dependency_list:
        source_table, source_column = dependency.split('.') if '.' in dependency else (None, dependency)
        data.append({
            "Column": col_name,
            "Column_Transformation": transformation,
            "Source_Table": source_table,
            "Source_Column": source_column
        })

# Prepare DataFrame for joins
join_data = []

for join in joins:
    join_data.append({
        "Join_Type": join["Join_Type"],
        "Left_Table": join["Left_Table"],
        "Right_Table": join["Right_Table"],
        "On_Condition": join["On_Condition"]
    })

# Prepare DataFrame for filters
filter_data = []

for where in filters:
    filter_data.append({
        "Filter_Condition": where.this.sql()
    })

# Create DataFrames
df = pd.DataFrame(data)
join_df = pd.DataFrame(join_data)
filter_df = pd.DataFrame(filter_data)

# Print DataFrames
print("Columns Information:")
print(df)
print("\nJoins Information:")
print(join_df)
print("\nFilters Information:")
print(filter_df)

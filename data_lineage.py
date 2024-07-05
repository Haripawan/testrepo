import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
import networkx as nx
import matplotlib.pyplot as plt

def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        sql_script = file.read()
    return sql_script

def parse_sql(sql_script):
    return sqlparse.parse(sql_script)

def is_subselect(parsed):
    if not parsed.is_group():
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False

def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            elif item.ttype is Keyword:
                return
            elif item.ttype is None:
                yield item
        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True

def extract_table_identifiers(token_stream):
    identifiers = []
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                identifiers.append(identifier.get_real_name())
        elif isinstance(item, Identifier):
            identifiers.append(item.get_real_name())
    return identifiers

def extract_table_column_references(parsed_sql):
    table_references = {}
    for statement in parsed_sql:
        if statement.get_type() == 'SELECT':
            tables = extract_table_identifiers(extract_from_part(statement))
            columns = []
            for token in statement.tokens:
                if isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        columns.append(identifier.get_real_name())
                elif isinstance(token, Identifier):
                    columns.append(token.get_real_name())
            for table in tables:
                if table not in table_references:
                    table_references[table] = set()
                table_references[table].update(columns)
    return table_references

def build_lineage_graph(table_references):
    G = nx.DiGraph()
    for table, columns in table_references.items():
        for column in columns:
            G.add_edge(column, table)
    return G

def visualize_graph(G):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=15, font_weight="bold")
    plt.title("Data Lineage Graph")
    plt.show()

# Example usage:
file_path = 'path_to_your_sql_file.sql'
sql_script = read_sql_file(file_path)
parsed_sql = parse_sql(sql_script)
table_references = extract_table_column_references(parsed_sql)
lineage_graph = build_lineage_graph(table_references)
visualize_graph(lineage_graph)


***************

import sqlparse

def extract_column_lineage(sql_query):
    parsed = sqlparse.parse(sql_query)
    statement = parsed[0]

    column_lineage = {}
    for token in statement.tokens:
        if token.ttype is None and token.is_group:
            for sub_token in token.tokens:
                if sub_token.ttype is None and sub_token.is_group:
                    for sub_sub_token in sub_token.tokens:
                        if sub_sub_token.ttype is None and sub_sub_token.is_group:
                            columns = [t.value for t in sub_sub_token.tokens if t.ttype is None]
                            if columns:
                                column_lineage['output'] = columns
                        elif sub_sub_token.ttype is None:
                            columns = [t.value for t in sub_sub_token.tokens if t.ttype is None]
                            if columns:
                                column_lineage['input'] = columns

    return column_lineage

sql_query = "SELECT a.col1, b.col2 FROM table1 a JOIN table2 b ON a.id = b.id"
lineage = extract_column_lineage(sql_query)
print(lineage)


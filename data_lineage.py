import sqlparse
import networkx as nx
import matplotlib.pyplot as plt

def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        sql_script = file.read()
    return sql_script

def parse_sql(sql_script):
    return sqlparse.parse(sql_script)

def extract_table_column_references(parsed_sql):
    table_references = {}
    for statement in parsed_sql:
        if statement.get_type() == 'SELECT':
            tables = [token.get_real_name() for token in statement.tokens if token.ttype is None and token.get_real_name()]
            columns = [token.get_real_name() for token in statement.tokens if token.ttype is not None and token.get_real_name()]
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
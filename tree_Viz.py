import networkx as nx
import matplotlib.pyplot as plt

# Example source-target mapping
edges = [
    ('A', 'B'),
    ('A', 'C'),
    ('B', 'D'),
    ('B', 'E'),
    ('C', 'F'),
    ('C', 'G'),
    ('E', 'H'),
    ('E', 'I')
]

# Create a directed graph from the edges
G = nx.DiGraph(edges)

# Circular layout for the nodes
pos = nx.circular_layout(G)

# Draw the nodes and edges with a circular layout
plt.figure(figsize=(8, 8))
nx.draw(G, pos, with_labels=True, arrows=True, node_size=2000, node_color='skyblue', font_size=15, font_weight='bold')
plt.title('Circular Tree Visualization for Source-Target Mapping')
plt.show()




import pandas as pd
from ete3 import Tree, TreeStyle, NodeStyle
from collections import defaultdict
import matplotlib.pyplot as plt

# Step 1: Load the data from Excel
file_path = 'your_excel_file.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Step 2: Generate distinct colors for each feed_id using matplotlib
unique_feeds = df['feed_id'].unique()
color_map = {feed_id: plt.cm.tab20(i / len(unique_feeds)) for i, feed_id in enumerate(unique_feeds)}

# Step 3: Create a single tree for all feeds
tree = Tree()
nodes = {}

for _, row in df.iterrows():
    feed_id = row['feed_id']
    source = row['source_app']
    target = row['target_app']
    
    if source not in nodes:
        nodes[source] = tree.add_child(name=source)
    if target not in nodes:
        nodes[target] = nodes[source].add_child(name=target)

    # Apply the color based on feed_id
    node_style = NodeStyle()
    node_style["size"] = 10
    r, g, b, _ = color_map[feed_id]  # Extract RGB values
    node_style["fgcolor"] = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
    nodes[target].set_style(node_style)

# Step 4: Define a tree style for circular layout
ts = TreeStyle()
ts.mode = "c"
ts.show_leaf_name = True
ts.show_branch_length = False
ts.show_branch_support = False

# Step 5: Render the combined tree and save it to a file
tree.render("combined_circular_tree.png", w=1000, tree_style=ts)



##################

import pandas as pd
from ete3 import Tree, TreeStyle, NodeStyle, TextFace, faces
from collections import defaultdict
import matplotlib.pyplot as plt

# Step 1: Load the data from Excel
file_path = 'your_excel_file.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Step 2: Generate distinct colors for each feed_id using matplotlib
unique_feeds = df['feed_id'].unique()
color_map = {feed_id: plt.cm.tab20(i / len(unique_feeds)) for i, feed_id in enumerate(unique_feeds)}

# Step 3: Create a single tree for all feeds
tree = Tree()
nodes = {}

# Function to wrap text
def wrap_text(text, length=10):
    return '\n'.join([text[i:i+length] for i in range(0, len(text), length)])

for _, row in df.iterrows():
    feed_id = row['feed_id']
    source = row['source_app']
    target = row['target_app']
    
    if source not in nodes:
        nodes[source] = tree.add_child(name=source)
    if target not in nodes:
        nodes[target] = nodes[source].add_child(name=target)

    # Apply the color based on feed_id and set node style
    node_style = NodeStyle()
    node_style["shape"] = "rectangle"
    node_style["size"] = 0
    node_style["fgcolor"] = "black"
    node_style["vt_line_width"] = 2  # Increase to add space vertically
    node_style["hz_line_width"] = 2  # Increase to add space horizontally
    node_style["vt_line_type"] = 0
    node_style["hz_line_type"] = 0
    node_style["bgcolor"] = f"#{int(color_map[feed_id][0] * 255):02x}{int(color_map[feed_id][1] * 255):02x}{int(color_map[feed_id][2] * 255):02x}"

    # Wrap text inside the box
    wrapped_text = wrap_text(nodes[target].name, length=10)
    text_face = TextFace(wrapped_text, fsize=10, fgcolor="black")
    
    # Add full text as tooltip/hover text (only for interactive environments like Jupyter)
    nodes[target].add_face(text_face, column=0, position="branch-right")
    
    # Attach the node style to the node
    nodes[target].set_style(node_style)

# Step 4: Define a tree style for circular layout
ts = TreeStyle()
ts.mode = "c"
ts.show_leaf_name = False  # Turn off default leaf names
ts.show_branch_length = False
ts.show_branch_support = False

# Increase margin around tree
ts.margin_left = 10
ts.margin_right = 10
ts.margin_top = 10
ts.margin_bottom = 10

# Step 5: Render the combined tree and save it to a file
tree.render("combined_circular_tree_with_boxes_wrapped.png", w=1200, tree_style=ts)

############################

import pandas as pd
from pycirclize import Circos
from pycirclize.parser import PhyloTree
import plotly.graph_objects as go

# Load the data from Excel
file_path = 'your_excel_file.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Create a newick-like string based on your data
def create_newick_string(df):
    newick = ""
    paths = {}
    for _, row in df.iterrows():
        source = row['source_app']
        target = row['target_app']
        feed_id = row['feed_id']
        if feed_id not in paths:
            paths[feed_id] = []
        paths[feed_id].append((source, target))

    for feed_id, path in paths.items():
        newick += "("
        for source, target in path:
            newick += f"({source},{target}),"
        newick = newick.rstrip(',') + ")"

    newick = newick.rstrip(',') + ";"
    return newick

newick_str = create_newick_string(df)

# Initialize Circos with PhyloTree
circos = Circos(sectors=PhyloTree(newick_str))

# Draw the tree using pycirclize
circos.plotfig(title="Circular Phylogenetic Tree")
circos.show()

# Moving to Plotly for Interactivity
# Generate positions for nodes based on the tree structure

# For simplicity, let's assume circular layout positions
def generate_positions(tree):
    from math import pi, cos, sin
    n = len(tree)
    positions = {}
    angle = 2 * pi / n
    for i, node in enumerate(tree.get_terminals()):
        positions[node.name] = (cos(i * angle), sin(i * angle))
    return positions

# Get terminal nodes positions
tree = PhyloTree(newick_str).tree
pos = generate_positions(tree)

# Plot with Plotly
edge_trace = []
for clade in tree.find_clades(order='level'):
    if clade.is_terminal():
        continue
    for child in clade:
        x0, y0 = pos[clade.name]
        x1, y1 = pos[child.name]
        edge_trace.append(
            go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
        )

node_trace = go.Scatter(
    x=[], y=[],
    text=[],
    mode='markers+text',
    textposition='bottom center',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

# Add nodes
for node in tree.get_terminals():
    x, y = pos[node.name]
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    node_trace['text'] += tuple([node.name])

# Add interactivity for node clicks
fig = go.Figure(data=edge_trace + [node_trace],
                layout=go.Layout(
                    title='<br>Interactive Circular Phylogenetic Tree',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="Click a node to highlight the path",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

# JavaScript for interaction
fig.update_traces(marker=dict(size=20), selector=dict(mode='markers'))
fig.update_layout(clickmode='event+select')

# Display the plot
fig.show()


##############

import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# Load your data
file_path = 'your_excel_file.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Create the directed graph
G = nx.DiGraph()

# Add edges to the graph
for _, row in df.iterrows():
    G.add_edge(row['source_app'], row['target_app'], feed_id=row['feed_id'])

# Generate positions for all nodes in a circular layout
pos = nx.circular_layout(G)

# Plotly visualization
edge_trace = []
for edge in G.edges(data=True):
    source, target, data = edge
    x0, y0 = pos[source]
    x1, y1 = pos[target]
    
    edge_trace.append(
        go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
    )

node_trace = go.Scatter(
    x=[], y=[],
    text=[], mode='markers+text',
    textposition='bottom center',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

# Add nodes
for node in G.nodes():
    x, y = pos[node]
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    node_trace['text'] += tuple([node])

# Add interactivity for node clicks
fig = go.Figure(data=edge_trace + [node_trace],
                layout=go.Layout(
                    title='<br>Interactive Circular Tree',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    annotations=[dict(
                        text="Click a node to highlight the path",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002)],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

# JavaScript for interaction
fig.update_traces(marker=dict(size=20), selector=dict(mode='markers'))
fig.update_layout(clickmode='event+select')

# Display the plot
fig.show()

####################

import pandas as pd
from ete3 import Tree, TreeStyle, NodeStyle, TextFace
from collections import defaultdict
import matplotlib.colors as mcolors

# Step 1: Load the data from Excel
file_path = 'your_excel_file.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Step 2: Organize data into a combined tree
combined_tree = Tree()
node_map = {}

# Define a color map for feed_ids
colors = list(mcolors.TABLEAU_COLORS.keys())  # Using Tableau colors
color_map = {feed_id: colors[i % len(colors)] for i, feed_id in enumerate(df['feed_id'].unique())}

# Step 3: Build the tree from the dataframe
for _, row in df.iterrows():
    source = row['source_app']
    target = row['target_app']
    feed_id = row['feed_id']
    
    # Add source node if not already present
    if source not in node_map:
        source_node = combined_tree.add_child(name=source)
        node_map[source] = source_node
    else:
        source_node = node_map[source]
    
    # Add target node if not already present
    if target not in node_map:
        target_node = source_node.add_child(name=target)
        node_map[target] = target_node
    else:
        target_node = node_map[target]

    # Apply color to each node based on the feed_id
    node_style = NodeStyle()
    node_style["size"] = 10
    node_style["fgcolor"] = color_map[feed_id]
    target_node.set_style(node_style)
    
    # Add a label to each node
    name_face = TextFace(target_node.name, fsize=10, fgcolor=color_map[feed_id])
    target_node.add_face(name_face, column=0, position="branch-right")

# Step 4: Visualize the combined tree
ts = TreeStyle()
ts.mode = "c"  # Circular mode
ts.show_leaf_name = False  # Names are displayed via TextFace, so this is redundant
ts.scale = 20  # Adjust scale to fit the tree nicely in the canvas

# Render the combined tree and save it to a file
output_file = "combined_tree.png"
combined_tree.render(output_file, w=1000, tree_style=ts)

print(f"Combined tree saved to {output_file}")

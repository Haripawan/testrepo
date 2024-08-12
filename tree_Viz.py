

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





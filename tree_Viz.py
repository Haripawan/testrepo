import pandas as pd
from ete3 import Tree, TreeStyle, NodeStyle
from collections import defaultdict

# Step 1: Load the data from Excel
file_path = 'your_excel_file.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Step 2: Organize data into a dictionary of trees, keyed by feed_id
feed_trees = defaultdict(lambda: Tree())

for feed_id in df['feed_id'].unique():
    feed_data = df[df['feed_id'] == feed_id]
    tree = Tree()
    nodes = {}
    
    for _, row in feed_data.iterrows():
        source = row['source_app']
        target = row['target_app']
        hop_number = row['hop_number']
        
        if source not in nodes:
            nodes[source] = tree.add_child(name=source)
        if target not in nodes:
            nodes[target] = nodes[source].add_child(name=target)
            
    feed_trees[feed_id] = tree

# Step 3: Define a color map for feed_ids
color_map = {
    feed_id: f"#{hex(1000000 + 2**feed_id)[2:]}"[:6]  # Generate unique colors based on feed_id
    for feed_id in df['feed_id'].unique()
}

# Step 4: Visualize each tree with color-coded nodes
for feed_id, tree in feed_trees.items():
    ts = TreeStyle()
    ts.mode = "c"
    ts.show_leaf_name = True
    
    # Apply color to each node based on the feed_id
    for node in tree.traverse():
        node_style = NodeStyle()
        node_style["size"] = 10
        node_style["fgcolor"] = color_map[feed_id]
        node.set_style(node_style)
    
    # Render the tree and save it to a file
    tree.render(f"circular_tree_feed_{feed_id}.png", w=800, tree_style=ts)
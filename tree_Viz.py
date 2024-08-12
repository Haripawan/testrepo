from ete3 import Tree, TreeStyle, NodeStyle

# Example of a multi-hierarchy tree in Newick format
newick = "((A:1,B:1):2,((C:1,D:1):2,(E:1,F:1,G:1):2):1);"

# Create a Tree object
tree = Tree(newick)

# Define a tree style for circular layout
ts = TreeStyle()
ts.mode = "c"  # Circular mode
ts.show_leaf_name = True  # Show leaf names
ts.show_branch_length = True  # Show branch lengths if needed
ts.show_branch_support = False  # Hide branch support values

# Customize individual nodes (optional)
for node in tree.traverse():
    node_style = NodeStyle()
    node_style["size"] = 10
    node_style["fgcolor"] = "black"
    node.set_style(node_style)

# Render the tree and save it to a file
tree.render("circular_tree_multihierarchy.png", w=800, tree_style=ts)
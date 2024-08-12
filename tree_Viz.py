from ete3 import Tree, TreeStyle, NodeStyle

# Example tree in Newick format
newick = "(((A,B),(C,D)),((E,F),(G,H)));"
tree = Tree(newick)

# Define a tree style
ts = TreeStyle()
ts.mode = "c"  # Circular mode

# Customize individual nodes
for n in tree.traverse():
    nstyle = NodeStyle()
    nstyle["fgcolor"] = "darkred"
    nstyle["size"] = 10
    n.set_style(nstyle)

# Render the tree
tree.render("advanced_circular_tree.png", w=800, tree_style=ts)
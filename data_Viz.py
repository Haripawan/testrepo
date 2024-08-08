import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Example DataFrame
data = {
    'unique_id': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7],
    'row_number': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
    'source_id': ['A', 'B', 'A', 'C', 'A', 'B', 'X', 'Y', 'A', 'B', 'X', 'Y', 'A', 'C'],
    'source_name': ['Source A', 'Target B', 'Source A', 'Target C', 'Source A', 'Target B', 
                    'Source X', 'Target Y', 'Source A', 'Target B', 'Source X', 'Target Y', 
                    'Source A', 'Target C'],
    'target_id': ['B', 'D', 'C', 'D', 'B', 'E', 'Y', 'Z', 'B', 'D', 'Y', 'Z', 
                  'C', 'F'],
    'target_name': ['Target B', 'Target D', 'Target C', 'Target D', 'Target B', 'Target E',
                    'Target Y', 'Target Z', 'Target B', 'Target D', 'Target Y', 'Target Z', 
                    'Target C', 'Target F']
}

df = pd.DataFrame(data)

# Group by source_name and target_name to count the number of unique_ids
grouped_df = df.groupby(['source_name', 'target_name']).agg({'unique_id': 'nunique'}).reset_index()

# Create a list of unique labels
all_labels = list(pd.concat([grouped_df['source_name'], grouped_df['target_name']]).unique())

# Create a dictionary to map source and target names to indices
label_indices = {name: i for i, name in enumerate(all_labels)}

# Prepare Sankey data
sankey_data = {
    'sources': grouped_df['source_name'].map(label_indices).tolist(),
    'targets': grouped_df['target_name'].map(label_indices).tolist(),
    'values': grouped_df['unique_id'].tolist(),
    'unique_ids': grouped_df['unique_id'].tolist()  # Keep unique IDs for coloring
}

# Generate a unique color for each unique ID
unique_ids = sorted(df['unique_id'].unique())
cmap = plt.get_cmap('tab20', len(unique_ids))  # Use a colormap with enough distinct colors
colors = [mcolors.to_hex(cmap(i)) for i in range(len(unique_ids))]
id_to_color = dict(zip(unique_ids, colors))

# Function to assign colors to links based on unique IDs
def assign_link_colors():
    return [id_to_color[uid] for uid in sankey_data['unique_ids']]

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='sankey-graph'),
])

@app.callback(
    Output('sankey-graph', 'figure'),
    [Input('sankey-graph', 'clickData')]
)
def update_graph(clickData):
    # Default colors
    link_colors = assign_link_colors()
    node_colors = ["rgba(31,119,180,0.6)"] * len(all_labels)
    
    if clickData and 'points' in clickData:
        clicked_node = clickData['points'][0].get('pointIndex')
        if clicked_node is not None:
            link_colors, node_colors = highlight_lineage(clicked_node)
    
    sankey = go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_labels,
            color=node_colors
        ),
        link=dict(
            source=sankey_data['sources'],
            target=sankey_data['targets'],
            value=sankey_data['values'],
            color=link_colors
        )
    )

    fig = go.Figure(sankey)
    fig.update_layout(title_text="Interactive Sankey Diagram with Lineage Highlighting", font_size=10)
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
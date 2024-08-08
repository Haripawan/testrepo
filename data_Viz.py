import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

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
    'values': grouped_df['unique_id'].tolist()
}

# Function to highlight a specific node's lineage
def highlight_lineage(selected_node):
    highlighted_link_colors = []
    highlighted_node_colors = ["rgba(31,119,180,0.6)"] * len(all_labels)

    for i, (src, tgt) in enumerate(zip(sankey_data['sources'], sankey_data['targets'])):
        if src == selected_node or tgt == selected_node:
            highlighted_link_colors.append("rgba(255,0,0,0.8)")  # Highlighted color
            highlighted_node_colors[src] = "rgba(255,0,0,0.8)"  # Highlight source node
            highlighted_node_colors[tgt] = "rgba(255,0,0,0.8)"  # Highlight target node
        else:
            highlighted_link_colors.append("rgba(200,200,200,0.4)")  # Dimmed color

    return highlighted_link_colors, highlighted_node_colors

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
    link_colors = ["rgba(31,119,180,0.6)"] * len(sankey_data['sources'])
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
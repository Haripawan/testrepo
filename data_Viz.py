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

# Generate unique colors for source nodes
unique_sources = sorted(df['source_name'].unique())
cmap = plt.get_cmap('tab20', len(unique_sources))  # Use a colormap with enough distinct colors
colors = [mcolors.to_hex(cmap(i)) for i in range(len(unique_sources))]
source_to_color = dict(zip(unique_sources, colors))

# Create Sankey diagrams for each unique identifier
def create_sankey_for_id(unique_id):
    # Filter data for the specific unique_id
    filtered_df = df[df['unique_id'] == unique_id]
    
    # Group by source_name and target_name to count the number of unique_ids
    grouped_df = filtered_df.groupby(['source_name', 'target_name']).agg({'unique_id': 'nunique'}).reset_index()
    
    # Create a list of unique labels
    all_labels = list(pd.concat([grouped_df['source_name'], grouped_df['target_name']]).unique())
    
    # Create a dictionary to map source and target names to indices
    label_indices = {name: i for i, name in enumerate(all_labels)}
    
    # Prepare Sankey data
    sankey_data = {
        'sources': grouped_df['source_name'].map(label_indices).tolist(),
        'targets': grouped_df['target_name'].map(label_indices).tolist(),
        'values': grouped_df['unique_id'].tolist(),
        'sources_names': grouped_df['source_name'].tolist()  # Keep source names for coloring
    }
    
    # Function to assign colors to nodes based on sources
    def assign_node_colors():
        node_colors = ["rgba(200,200,200,0.6)"] * len(all_labels)
        for source, color in source_to_color.items():
            if source in label_indices:
                node_colors[label_indices[source]] = color
        return node_colors
    
    # Function to assign colors to links based on sources
    def assign_link_colors():
        return [source_to_color.get(source, "rgba(200,200,200,0.4)") for source in sankey_data['sources_names']]
    
    # Create the Sankey diagram
    sankey = go.Sankey(
        node=dict(
            pad=30,
            thickness=30,
            line=dict(color="black", width=0.5),
            label=all_labels,
            color=assign_node_colors()
        ),
        link=dict(
            source=sankey_data['sources'],
            target=sankey_data['targets'],
            value=sankey_data['values'],
            color=assign_link_colors()
        )
    )
    
    fig = go.Figure(sankey)
    fig.update_layout(title_text=f"Sankey Diagram for Unique ID {unique_id}", font_size=10)
    return fig

# Initialize the Dash app
app = dash.Dash(__name__)

# Get unique IDs for tabs
unique_ids = df['unique_id'].unique()

# Create tabs for each unique ID
tabs = [dcc.Tab(label=f"ID {uid}", value=uid) for uid in unique_ids]

app.layout = html.Div([
    dcc.Tabs(id='tabs', value=unique_ids[0], children=tabs, style={'width': '100%'}),
    html.Div(id='tab-content', style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '90vh', 'overflow': 'auto'})
])

@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'value')]
)
def update_tab(selected_id):
    fig = create_sankey_for_id(selected_id)
    return dcc.Graph(figure=fig, style={'height': '90vh', 'width': '100%'})

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
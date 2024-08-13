import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

# Function to create the chord diagram
def create_chord_diagram(matrix, labels):
    # Normalize the matrix for better visualization
    matrix = np.array(matrix)
    total_sum = np.sum(matrix)
    matrix = matrix / total_sum

    # Initialize the chord diagram
    fig = make_subplots(specs=[[{"type": "polar"}]])

    # Number of nodes
    num_nodes = len(labels)

    # Angles and widths for each node
    angles = np.linspace(0, 2 * np.pi, num_nodes, endpoint=False)
    widths = np.sum(matrix, axis=1) / np.sum(matrix)

    # Draw the arcs for each node
    for i, (label, angle, width) in enumerate(zip(labels, angles, widths)):
        theta0 = np.degrees(angle)
        theta1 = np.degrees(angle + width * 2 * np.pi)
        fig.add_trace(go.Barpolar(
            r=[1],
            theta=[(theta0 + theta1) / 2],
            width=[width * 360],
            marker_color='rgba(200,200,200,0.5)',
            marker_line_color='black',
            marker_line_width=2,
            opacity=0.6,
            name=label
        ))

    # Draw the connections (chords)
    for i in range(num_nodes):
        for j in range(i+1, num_nodes):
            value = matrix[i, j]
            if value > 0:
                fig.add_trace(go.Scatterpolar(
                    r=[0, 1, 1, 0],
                    theta=[angles[i]*180/np.pi, angles[i]*180/np.pi, angles[j]*180/np.pi, angles[j]*180/np.pi],
                    fill='toself',
                    fillcolor=f'rgba(255, 0, 0, {value})',
                    line=dict(color='rgba(255,0,0,0)'),
                    opacity=0.4
                ))

    # Update layout
    fig.update_layout(
        showlegend=False,
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(visible=False)
        )
    )

    return fig

# Labels for the nodes
labels = data.columns.tolist()

# Create the chord diagram
fig = create_chord_diagram(data, labels)

# Display the chord diagram
fig.show()
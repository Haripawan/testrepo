// Sample data
const data = {
    nodes: [
        { id: 1, title: "Node 1", columns: ["Column 1", "Column 2", "Column 3"], expanded: true },
        { id: 2, title: "Node 2", columns: ["Column 1", "Column 2", "Column 3"], expanded: true },
        { id: 3, title: "Node 3", columns: ["Column 1", "Column 2", "Column 3"], expanded: true },
    ],
    links: [
        { source: { node: 1, column: "Column 1" }, target: { node: 3, column: "Column 1" } },
        { source: { node: 2, column: "Column 2" }, target: { node: 3, column: "Column 2" } },
    ]
};

// Function to create nodes
function createNodes(container, nodes) {
    nodes.forEach((node, index) => {
        const nodeEl = document.createElement('div');
        nodeEl.className = 'node';

        if (index === 2) {
            nodeEl.style.left = `50%`;
            nodeEl.style.top = `50%`;
            nodeEl.style.transform = `translate(-50%, -50%)`;
        } else {
            nodeEl.style.left = `50px`; // Position first two nodes to the left
            nodeEl.style.top = `${50 + index * 180}px`; // Stack the first two nodes vertically
        }

        const titleEl = document.createElement('div');
        titleEl.className = 'node-title';
        titleEl.innerText = node.title;

        const actionsEl = document.createElement('div');
        actionsEl.className = 'actions';
        
        const collapseExpandEl = document.createElement('span');
        collapseExpandEl.innerText = node.expanded ? '-' : '+';
        collapseExpandEl.addEventListener('click', () => {
            node.expanded = !node.expanded;
            collapseExpandEl.innerText = node.expanded ? '-' : '+';
            columnsEl.style.display = node.expanded ? 'block' : 'none';
            drawLinks();
        });

        const lineageEl = document.createElement('span');
        lineageEl.innerText = '→';
        // Implement lineage click action if needed

        actionsEl.appendChild(collapseExpandEl);
        actionsEl.appendChild(lineageEl);
        titleEl.appendChild(actionsEl);

        const columnsEl = document.createElement('ul');
        columnsEl.className = 'node-columns';
        columnsEl.style.display = node.expanded ? 'block' : 'none';
        node.columns.forEach(col => {
            const colEl = document.createElement('li');
            colEl.innerText = col;
            colEl.addEventListener('click', () => {
                highlightLinks(node.id, col);
            });
            columnsEl.appendChild(colEl);
        });

        nodeEl.appendChild(titleEl);
        nodeEl.appendChild(columnsEl);
        container.appendChild(nodeEl);
        
        node.element = nodeEl; // Store the element reference
    });
}

// Create SVG links between nodes
function drawLinks() {
    const svg = d3.select("#svgContainer");
    svg.selectAll("*").remove(); // Clear previous links

    // Clear previous highlights
    document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));

    data.links.forEach(link => {
        const sourceNode = data.nodes.find(n => n.id === link.source.node);
        const targetNode = data.nodes.find(n => n.id === link.target.node);

        const sourceElement = sourceNode.expanded
            ? Array.from(sourceNode.element.querySelectorAll('.node-columns li')).find(el => el.innerText === link.source.column)
            : sourceNode.element.querySelector('.node-title');
        
        const targetElement = targetNode.expanded
            ? Array.from(targetNode.element.querySelectorAll('.node-columns li')).find(el => el.innerText === link.target.column)
            : targetNode.element.querySelector('.node-title');

        const sourcePos = getElementCenter(sourceElement);
        const targetPos = getElementCenter(targetElement);

        const pathData = generatePathData(sourcePos, targetPos);

        svg.append("path")
            .attr("d", pathData)
            .attr("stroke", "black")
            .attr("stroke-width", 2)
            .attr("fill", "none");

        // Highlight columns involved in the linkage
        if (sourceNode.expanded) sourceElement.classList.add('highlight');
        if (targetNode.expanded) targetElement.classList.add('highlight');
    });
}

// Function to get the center of an element
function getElementCenter(element) {
    const rect = element.getBoundingClientRect();
    return {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
    };
}

// Function to generate right-angle path data
function generatePathData(source, target) {
    const midX = (source.x + target.x) / 2;
    return `M${source.x},${source.y} 
            L${midX},${source.y} 
            L${midX},${target.y} 
            L${target.x},${target.y}`;
}

// Function to highlight links
function highlightLinks(nodeId, columnName) {
    document.querySelectorAll('path').forEach(path => path.classList.remove('line-highlight'));
    data.links.forEach(link => {
        if ((link.source.node === nodeId && link.source.column === columnName) ||
            (link.target.node === nodeId && link.target.column === columnName)) {
            const sourceNode = data.nodes.find(n => n.id === link.source.node);
            const targetNode = data.nodes.find(n => n.id === link.target.node);
            const sourceElement = sourceNode.expanded
                ? Array.from(sourceNode.element.querySelectorAll('.node-columns li')).find(el => el.innerText === link.source.column)
                : sourceNode.element.querySelector('.node-title');
            const targetElement = targetNode.expanded
                ? Array.from(targetNode.element.querySelectorAll('.node-columns li')). find(el => el.innerText === link.target.column)
                : targetNode.element.querySelector('.node-title');
            const sourcePos = getElementCenter(sourceElement);
            const targetPos = getElementCenter(targetElement);
            const pathData = generatePathData(sourcePos, targetPos);
            d3.select('svg').append("path")
                .attr("d", pathData)
                .attr("stroke", "orange")
                .attr("stroke-width", 4)
                .attr("fill", "none")
                .classed('line-highlight', true);
        }
    });
}

// Center the lineage container and update node positions
function centerLineage() {
    const container = document.getElementById('lineage-container');
    const totalHeight = data.nodes.length * 180; // Adjust based on node height and spacing
    const viewportHeight = window.innerHeight;
    const topOffset = (viewportHeight - totalHeight) / 2;
    container.style.top = `${topOffset}px`;

    // Update node positions after centering
    updateNodePositions();
}

// Function to update node positions
function updateNodePositions() {
    data.nodes.forEach((node, index) => {
        const nodeEl = node.element;
        if (index === 2) {
            nodeEl.style.left = `50%`;
            nodeEl.style.top = `50%`;
            nodeEl.style.transform = `translate(-50%, -50%)`;
        } else {
            nodeEl.style.left = `50px`; // Position first two nodes to the left
            nodeEl.style.top = `${50 + index * 180}px`; // Stack the first two nodes vertically
        }
    });

    // Redraw links after updating node positions
    drawLinks();
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('lineage-container');
    createNodes(container, data.nodes);
    drawLinks();
    centerLineage();

    // Recenter and update node positions on window resize
    window.addEventListener('resize', () => {
        centerLineage();
    });
});
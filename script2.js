// Sample data
const data = {
    nodes: [
        { id: 1, title: "Node 1", columns: ["Column 1", "Column 2", "Column 3"], expanded: true },
        { id: 2, title: "Node 2", columns: ["Column 1", "Column 2", "Column 3"], expanded: true },
        { id: 3, title: "Node 3", columns: ["Column 1", "Column 2", "Column 3"], expanded: true },
    ],
    links: [
        { source: { node: 1, column: "Column 1" }, target: { node: 2, column: "Column 1" } },
        { source: { node: 2, column: "Column 2" }, target: { node: 3, column: "Column 2" } },
    ]
};

// Function to create nodes
function createNodes(container, nodes) {
    nodes.forEach((node, index) => {
        const nodeEl = document.createElement('div');
        nodeEl.className = 'node';
        nodeEl.style.left = `${index * 240}px`; // Adjust horizontal spacing as needed
        nodeEl.style.top = `50%`;
        nodeEl.style.transform = `translateY(-50%)`;

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
            columnsEl.appendChild(colEl);
        });

        nodeEl.appendChild(titleEl);
        nodeEl.appendChild(columnsEl);
        container.appendChild(nodeEl);
        
        // Make the node draggable
        nodeEl.draggable = true;
        nodeEl.ondragstart = dragStart;
        nodeEl.ondragend = dragEnd;
        
        node.element = nodeEl; // Store the element reference
    });
}

// Drag and Drop Functions
let currentDragNode = null;

function dragStart(event) {
    currentDragNode = event.target;
    event.dataTransfer.setData('text/plain', '');
}

function dragEnd(event) {
    currentDragNode.style.left = `${event.clientX - currentDragNode.offsetWidth / 2}px`;
    currentDragNode.style.top = `${event.clientY - currentDragNode.offsetHeight / 2}px`;
    currentDragNode = null;
    drawLinks();
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
            .attr("fill", "none");

        // Highlight columns involved in the linkage
        if (sourceNode.expanded) sourceElement.classList.add('highlight');
        if (targetNode.expanded) targetElement.classList.add('highlight');
    });
}

function getElementCenter(element) {
    const rect = element.getBoundingClientRect();
    return {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
    };
}

function generatePathData(source, target) {
    const midX = (source.x + target.x) / 2;
    const midY = (source.y + target.y) / 2;
    const curveOffset = 50;

    return `M${source.x},${source.y} 
            C${midX - curveOffset},${source.y} 
             ${midX + curveOffset},${target.y} 
             ${target.x},${target.y}`;
}

// Center the lineage container
function centerLineage() {
    const container = document.getElementById('lineage-container');
    const containerRect = container.getBoundingClientRect();
    const totalWidth = data.nodes.length * 240; // Adjust based on node width and spacing
    const leftOffset = (containerRect.width - totalWidth) / 2;
    container.style.left = `${leftOffset}px`;
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('lineage-container');
    createNodes(container, data.nodes);
    drawLinks();
    centerLineage();
});
// Sample data
const data = {
    nodes: [
        { id: 1, title: "Node 1", columns: ["Column 1", "Column 2", "Column 3"] },
        { id: 2, title: "Node 2", columns: ["Column 1", "Column 2", "Column 3"] },
        { id: 3, title: "Node 3", columns: ["Column 1", "Column 2", "Column 3"] },
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
        titleEl.addEventListener('click', () => {
            columnsEl.style.display = columnsEl.style.display === 'none' ? 'block' : 'none';
            drawLinks();
        });

        const columnsEl = document.createElement('ul');
        columnsEl.className = 'node-columns';
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

    const lineGenerator = d3.line()
        .x(d => d.x)
        .y(d => d.y)
        .curve(d3.curveBasis);

    data.links.forEach(link => {
        const sourceNode = data.nodes.find(n => n.id === link.source.node);
        const targetNode = data.nodes.find(n => n.id === link.target.node);

        const sourceElement = Array.from(sourceNode.element.querySelectorAll('.node-columns li'))
            .find(el => el.innerText === link.source.column);
        const targetElement = Array.from(targetNode.element.querySelectorAll('.node-columns li'))
            .find(el => el.innerText === link.target.column);

        const sourcePos = getElementCenter(sourceElement);
        const targetPos = getElementCenter(targetElement);

        const pathData = lineGenerator([sourcePos, targetPos]);

        svg.append("path")
            .attr("d", pathData)
            .attr("stroke", "black")
            .attr("fill", "none");
    });
}

function getElementCenter(element) {
    const rect = element.getBoundingClientRect();
    return {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
    };
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('lineage-container');
    createNodes(container, data.nodes);
    drawLinks();
});
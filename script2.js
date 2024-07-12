// Sample data
const data = {
    nodes: [
        { id: 1, title: "Node 1", columns: ["Column 1", "Column 2", "Column 3"] },
        { id: 2, title: "Node 2", columns: ["Column 1", "Column 2", "Column 3"] },
        { id: 3, title: "Node 3", columns: ["Column 1", "Column 2", "Column 3"] },
    ],
    links: [
        { source: 1, target: 2 },
        { source: 2, target: 3 },
    ]
};

// Function to create nodes
function createNodes(container, nodes) {
    nodes.forEach((node, index) => {
        const nodeEl = document.createElement('div');
        nodeEl.className = 'node';
        nodeEl.style.left = `${index * 220}px`; // Adjust horizontal spacing as needed
        nodeEl.style.top = `50%`;
        nodeEl.style.transform = `translateY(-50%)`;

        const titleEl = document.createElement('div');
        titleEl.className = 'node-title';
        titleEl.innerText = node.title;
        titleEl.addEventListener('click', () => {
            columnsEl.style.display = columnsEl.style.display === 'none' ? 'block' : 'none';
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
}

// Create SVG links between nodes
function createLinks(svg, links, nodes) {
    const lineGenerator = d3.line()
        .x(d => d.x)
        .y(d => d.y)
        .curve(d3.curveBasis);

    links.forEach(link => {
        const sourceNode = nodes.find(n => n.id === link.source);
        const targetNode = nodes.find(n => n.id === link.target);
        
        const sourcePos = getElementCenter(sourceNode.element);
        const targetPos = getElementCenter(targetNode.element);

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
    const svg = d3.select("#svgContainer");
    createNodes(container, data.nodes);
    createLinks(svg, data.links, data.nodes.map(node => ({
        id: node.id,
        element: document.querySelector(`.node:nth-child(${node.id})`)
    })));
});
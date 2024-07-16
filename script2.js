// Function to fetch JSON data and initialize the lineage visualization
function fetchDataAndInitialize() {
    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            createNodesAndLinks(data);
        })
        .catch(error => console.error('Error loading JSON data:', error));
}

// Function to create nodes and links
function createNodesAndLinks(data) {
    const container = document.getElementById('lineage-container');
    const containerWidth = container.clientWidth;

    const horizontalSpacing = 300; // Adjust horizontal spacing
    const verticalSpacing = 180; // Adjust vertical spacing
    const nodesMap = new Map();

    // Position nodes based on their hierarchical level
    data.nodes.forEach((node, index) => {
        const nodeEl = document.createElement('div');
        nodeEl.className = 'node';
        nodesMap.set(node.id, nodeEl);

        // Position node
        const nodeLevel = getNodeLevel(node.id, data.links);
        nodeEl.style.left = `${nodeLevel * horizontalSpacing}px`;
        nodeEl.style.top = `${50 + index * verticalSpacing}px`;

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
            drawLinks(data, nodesMap);
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
                highlightLinks(node.id, col, data, nodesMap);
            });
            columnsEl.appendChild(colEl);
        });

        nodeEl.appendChild(titleEl);
        nodeEl.appendChild(columnsEl);
        container.appendChild(nodeEl);
        
        node.element = nodeEl; // Store the element reference
    });

    drawLinks(data, nodesMap);
    centerLineage(container, data.nodes.length, verticalSpacing);
}

// Function to determine the level of a node based on its connections
function getNodeLevel(nodeId, links) {
    const sourceLinks = links.filter(link => link.source.node === nodeId);
    const targetLinks = links.filter(link => link.target.node === nodeId);

    if (sourceLinks.length === 0 && targetLinks.length === 0) {
        return 0; // No links, standalone node
    }

    if (targetLinks.length === 0) {
        return 1; // Source node
    }

    const levels = targetLinks.map(link => getNodeLevel(link.source.node, links));
    return Math.max(...levels) + 1;
}

// Function to create SVG links between nodes
function drawLinks(data, nodesMap) {
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
function highlightLinks(nodeId, columnName, data, nodesMap) {
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

// Center the lineage container
function centerLineage(container, nodeCount, verticalSpacing) {
    const totalHeight = nodeCount * verticalSpacing; // Adjust based on node height and spacing
    const viewportHeight = window.innerHeight;
    const topOffset = (viewportHeight - totalHeight) / 2;
    container.style.top = `${topOffset}px`;
}

// Initialize
document.addEventListener("DOMContentLoaded", fetchDataAndInitialize);
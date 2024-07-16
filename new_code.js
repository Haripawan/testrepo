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

// Function to create nodes based on links
function createNodes(container, nodes, links) {
    // Sort nodes based on links to determine order
    const sortedNodes = sortNodesByLinks(nodes, links);

    // Calculate positions for nodes
    const nodePositions = calculateNodePositions(sortedNodes);

    // Create nodes
    sortedNodes.forEach((node, index) => {
        const nodeEl = document.createElement('div');
        nodeEl.className = 'node';
        nodeEl.style.left = `${nodePositions[index].x}px`;
        nodeEl.style.top = `${nodePositions[index].y}px`;

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
                toggleHighlight(node.id, col, colEl);
            });
            columnsEl.appendChild(colEl);
        });

        nodeEl.appendChild(titleEl);
        nodeEl.appendChild(columnsEl);
        container.appendChild(nodeEl);
        
        node.element = nodeEl; // Store the element reference
    });

    // Redraw links after creating nodes
    drawLinks();
}

// Function to sort nodes based on links to determine left-right positioning
function sortNodesByLinks(nodes, links) {
    const nodeMap = new Map(nodes.map(node => [node.id, node]));
    const sortedNodes = [];

    // Starting with nodes that are source only
    const sourceNodes = nodes.filter(node => !links.some(link => link.target.node === node.id));
    sourceNodes.forEach(node => {
        sortedNodes.push(node);
        addConnectedNodes(node.id, sortedNodes, links, nodeMap, 'target');
    });

    return sortedNodes;
}

// Recursive function to add connected nodes
function addConnectedNodes(nodeId, sortedNodes, links, nodeMap, direction) {
    const connectedLinks = links.filter(link => link[direction].node === nodeId);
    connectedLinks.forEach(link => {
        const connectedNode = nodeMap.get(link[direction === 'source' ? 'target' : 'source'].node);
        if (!sortedNodes.includes(connectedNode)) {
            sortedNodes.push(connectedNode);
            addConnectedNodes(connectedNode.id, sortedNodes, links, nodeMap, direction);
        }
    });
}

// Function to calculate node positions
function calculateNodePositions(nodes) {
    const nodePositions = [];
    const totalNodes = nodes.length;
    const spacingY = 180;
    const leftMargin = 50;
    const rightMargin = 50;
    const canvasHeight = window.innerHeight - 100; // Adjust as needed

    const centerY = canvasHeight / 2;
    const leftNodesCount = nodes.filter(node => !node.links.some(link => link.target === node.id)).length;
    const rightNodesCount = totalNodes - leftNodesCount;

    let leftIndex = 0;
    let rightIndex = 0;

    nodes.forEach((node, index) => {
        if (!node.links.some(link => link.target === node.id)) {
            // Node is a source node
            const y = centerY - ((leftNodesCount - 1) / 2 - leftIndex) * spacingY;
            nodePositions.push({ x: leftMargin, y: y });
            leftIndex++;
        } else {
            // Node is a target node
            const y = centerY - ((rightNodesCount - 1) / 2 - rightIndex) * spacingY;
            nodePositions.push({ x: window.innerWidth - rightMargin, y: y });
            rightIndex++;
        }
    });

    return nodePositions;
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

// Function to generate curved path data
function generatePathData(source, target) {
    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const xOffset = dx * 0.6; // Adjust the curve intensity
    const yOffset = dy * 0.6; // Adjust the curve intensity

    // Bezier curve path
    return `M${source.x},${source.y} C${source.x + xOffset},${source.y} ${target.x - xOffset},${target.y} ${target.x},${target.y}`;
}

// Function to toggle highlight on paths and columns
function toggleHighlight(nodeId, columnName, columnElement) {
    const svg = d3.select("#svgContainer");
    const paths = svg.selectAll("path");

    const highlightedPaths = paths.filter(function() {
        return d3.select(this).classed('line-highlight');
    });

    const isAlreadyHighlighted = columnElement.classList.contains('highlight');

    if (isAlreadyHighlighted) {
        // Remove highlights
        highlightedPaths.classed('line-highlight', false);
        columnElement.classList.remove('highlight');
    } else {
        // Clear previous highlights
        paths.classed('line-highlight', false);
        document.querySelectorAll('.node-columns li').forEach(el => el.classList.remove('highlight'));

        // Highlight the paths and columns
        data.links.forEach(link => {
            if ((link.source.node === nodeId && link.source.column === columnName) ||
                (link.target.node === nodeId && link.target.column === columnName)) {
                
                const sourceNode = data.nodes.find(n => n.id === link.source.node);
                const targetNode = data.nodes.find(n => n.id === link.target.node);

                const sourceElement = sourceNode.expanded
                    ? Array.from(sourceNode.element.querySelectorAll('.node-columns li')).find(el => el.innerText === link.source.column)
                    : sourceNode.element.querySelector('.node-title');
                
                const targetElement = targetNode.expanded
                    ? Array.from(targetNode.element.querySelectorAll('.node-columns li')).find(el => el.innerText === link.target.column)
                    : targetNode.element.querySelector('.node-title');

                // Highlight path
                paths.filter(function() {
                    const d = d3.select(this).attr("d");
                    const sourcePos = getElementCenter(sourceElement);
                    const targetPos = getElementCenter(targetElement);
                    const pathData = generatePathData(sourcePos, targetPos);
                    return d === pathData;
                }).classed('line-highlight', true);
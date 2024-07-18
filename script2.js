// Function to fetch JSON data and initialize the lineage visualization
function fetchDataAndInitialize() {
    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            window.currentData = data; // Store data globally for expand/collapse functions
            createNodesAndLinks(data);
            centerLineage();
            window.addEventListener('resize', centerLineage); // Recenter on window resize
        })
        .catch(error => console.error('Error loading JSON data:', error));
}

// Function to create nodes and links
function createNodesAndLinks(data) {
    const container = document.getElementById('lineage-container');
    container.innerHTML = ''; // Clear previous content

    const horizontalSpacing = 300; // Adjust horizontal spacing
    const verticalSpacing = 180; // Adjust vertical spacing
    const nodesMap = new Map();

    // Calculate the levels of each node
    const nodeLevels = calculateNodeLevels(data.links);
    const maxLevel = Math.max(...Object.values(nodeLevels));

    // Position nodes based on their hierarchical level
    const nodePosition = {};
    data.nodes.forEach((node, index) => {
        const nodeEl = document.createElement('div');
        nodeEl.className = 'node';
        nodesMap.set(node.id, nodeEl);

        // Position node
        const nodeLevel = nodeLevels[node.id];
        if (!nodePosition[nodeLevel]) {
            nodePosition[nodeLevel] = 0;
        }
        const nodeIndex = nodePosition[nodeLevel]++;
        
        nodeEl.style.left = `${nodeLevel * horizontalSpacing}px`;
        nodeEl.style.top = `${50 + nodeIndex * verticalSpacing}px`;

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

        actionsEl.appendChild(collapseExpandEl);
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
}

// Function to calculate the levels of each node
function calculateNodeLevels(links) {
    const nodeLevels = {};

    function setNodeLevel(nodeId, level) {
        if (nodeLevels[nodeId] == null || nodeLevels[nodeId] < level) {
            nodeLevels[nodeId] = level;
            links.filter(link => link.source.node === nodeId)
                .forEach(link => setNodeLevel(link.target.node, level + 1));
        }
    }

    links.forEach(link => {
        setNodeLevel(link.source.node, 0);
    });

    return nodeLevels;
}

// Function to create SVG links between nodes
function drawLinks(data, nodesMap) {
    const svgContainer = d3.select("#svgContainer");
    svgContainer.selectAll("*").remove(); // Clear previous links

    const svgWidth = document.getElementById('lineage-container').scrollWidth;
    const svgHeight = document.getElementById('lineage-container').scrollHeight;

    const svg = svgContainer.append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight);

    data.links.forEach(link => {
        const sourceNode = data.nodes.find(n => n.id === link.source.node);
        const targetNode = data.nodes.find(n => n.id === link.target.node);

        if (!sourceNode || !targetNode) {
            console.error('Invalid link:', link);
            return;
        }

        const sourceElement = sourceNode.expanded
            ? Array.from(sourceNode.element.querySelectorAll('.node-columns li')).find(el => el.innerText === link.source.column)
            : sourceNode.element.querySelector('.node-title');
        
        const targetElement = targetNode.expanded
            ? Array.from(targetNode.element.querySelectorAll('.node-columns li')).find(el => el.innerText === link.target.column)
            : targetNode.element.querySelector('.node-title');

        if (!sourceElement || !targetElement) {
            console.error('Invalid source/target element for link:', link);
            return;
        }

        const sourcePos = getElementCenter(sourceElement);
        const targetPos = getElementCenter(targetElement);

        const pathData = generatePathData(sourcePos, targetPos);

        svg.append("path")
            .attr("d", pathData)
            .attr("stroke", "black")
            .attr("stroke-width", 2)
            .attr("fill", "none");
    });
}

// Function to get the center of an element
function getElementCenter(element) {
    const rect = element.getBoundingClientRect();
    return {
        x: rect.left + rect.width / 2 + window.scrollX,
        y: rect.top + rect.height / 2 + window.scrollY
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

// Function to center the lineage visualization
function centerLineage() {
    const container = document.getElementById('lineage-container');
    const boundingRect = container.getBoundingClientRect();
    const offsetX = (window.innerWidth - boundingRect.width) / 2 - boundingRect.left;
    const offsetY = (window.innerHeight - boundingRect.height) / 2 - boundingRect.top;
    container.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
}

// Function to expand all nodes
function expandAll() {
    const data = window.currentData;
    data.nodes.forEach(node => node.expanded = true);
    createNodesAndLinks(data);
}

// Function to collapse all nodes
function collapseAll() {
    const data = window.currentData;
    data.nodes.forEach(node => node.expanded = false);
    createNodesAndLinks(data);
}

// Function to toggle the sidebar menu
function toggleMenu() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('open');
}

// Function to show the lineage page
function showPage(pageId) {
    const pages = document.querySelectorAll('.content > div');
    pages.forEach(page => {
        if (page.id === pageId) {
            page.style.display = 'block';
        } else {
            page.style.display = 'none';
        }
    });
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    fetchDataAndInitialize();
    document.getElementById('expand-all').addEventListener('click', expandAll);
    document.getElementById('collapse-all').addEventListener('click', collapseAll);
});
// Fetch JSON data and initialize the lineage visualization
fetch('data.json')
    .then(response => response.json())
    .then(data => {
        // Function to create nodes
        function createNodes(container, nodes) {
            // Get the width of the container
            const containerWidth = container.clientWidth;

            // Separate nodes into source and target based on links
            const sourceNodeIds = new Set(data.links.map(link => link.source.node));
            const targetNodeIds = new Set(data.links.map(link => link.target.node));

            let sourceIndex = 0;
            let targetIndex = 0;

            // Adjust these values to change spacing
            const horizontalSpacing = 200; // Adjust horizontal spacing between source and target nodes
            const verticalSpacing = 180; // Adjust vertical spacing between nodes

            nodes.forEach(node => {
                const nodeEl = document.createElement('div');
                nodeEl.className = 'node';

                // Position source nodes on the left and target nodes on the right
                if (sourceNodeIds.has(node.id)) {
                    nodeEl.style.left = `50px`; // Left side for source nodes
                    nodeEl.style.top = `${50 + sourceIndex * verticalSpacing}px`; // Adjust vertical position
                    sourceIndex++;
                } else if (targetNodeIds.has(node.id)) {
                    nodeEl.style.left = `${containerWidth - horizontalSpacing}px`; // Right side for target nodes, adjust horizontal position
                    nodeEl.style.top = `${50 + targetIndex * verticalSpacing}px`; // Adjust vertical position
                    targetIndex++;
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
                    ? Array.from(targetNode.element.querySelectorAll('.node-columns li')). find(el => el.innerText === link.target.column)
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

        // Center the lineage container
        function centerLineage() {
            const container = document.getElementById('lineage-container');
            const totalHeight = data.nodes.length * verticalSpacing; // Adjust based on node height and spacing
            const viewportHeight = window.innerHeight;
            const topOffset = (viewportHeight - totalHeight) / 2;
            container.style.top = `${topOffset}px`;
        }

        // Initialize
        document.addEventListener("DOMContentLoaded", () => {
            const container = document.getElementById('lineage-container');
            createNodes(container, data.nodes);
            drawLinks();
            centerLineage();
            window.addEventListener('resize', centerLineage); // Recenter on window resize
        });
    })
    .catch(error => console.error('Error loading JSON data:', error));
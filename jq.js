$(document).ready(function() {
    function fetchDataAndInitialize() {
        $.getJSON('data.json', function(data) {
            window.currentData = data; // Store data globally for expand/collapse functions
            createNodesAndLinks(data);
            centerLineage();
            $(window).resize(centerLineage); // Recenter on window resize
        }).fail(function() {
            console.error('Error loading JSON data');
        });
    }

    function createNodesAndLinks(data) {
        const $container = $('#lineage-container');
        $container.empty(); // Clear previous content

        const horizontalSpacing = 300; // Adjust horizontal spacing
        const verticalSpacing = 180; // Adjust vertical spacing
        const nodesMap = new Map();

        const nodeLevels = calculateNodeLevels(data.links);
        const maxLevel = Math.max(...Object.values(nodeLevels));

        const nodePosition = {};
        data.nodes.forEach(node => {
            const $nodeEl = $('<div>').addClass('node');
            nodesMap.set(node.id, $nodeEl);

            const nodeLevel = nodeLevels[node.id];
            if (!nodePosition[nodeLevel]) {
                nodePosition[nodeLevel] = 0;
            }
            const nodeIndex = nodePosition[nodeLevel]++;

            $nodeEl.css({
                left: `${nodeLevel * horizontalSpacing}px`,
                top: `${50 + nodeIndex * verticalSpacing}px`
            });

            const $titleEl = $('<div>').addClass('node-title').text(node.title);
            const $actionsEl = $('<div>').addClass('actions');

            const $collapseExpandEl = $('<span>').text(node.expanded ? '-' : '+');
            $collapseExpandEl.on('click', function() {
                node.expanded = !node.expanded;
                $collapseExpandEl.text(node.expanded ? '-' : '+');
                $columnsEl.toggle(node.expanded);
                drawLinks(data, nodesMap);
            });

            $actionsEl.append($collapseExpandEl);
            $titleEl.append($actionsEl);

            const $columnsEl = $('<ul>').addClass('node-columns').toggle(node.expanded);
            node.columns.forEach(col => {
                const $colEl = $('<li>').text(col);
                $colEl.on('click', function() {
                    highlightLinks(node.id, col, data, nodesMap);
                });
                $columnsEl.append($colEl);
            });

            $nodeEl.append($titleEl).append($columnsEl);
            $container.append($nodeEl);

            node.element = $nodeEl[0]; // Store the element reference
        });

        drawLinks(data, nodesMap);
    }

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

    function drawLinks(data, nodesMap) {
        const $svgContainer = $("#svgContainer");
        $svgContainer.empty(); // Clear previous links

        const svgWidth = $('#lineage-container').prop('scrollWidth');
        const svgHeight = $('#lineage-container').prop('scrollHeight');

        const $svg = $('<svg>').attr({
            width: svgWidth,
            height: svgHeight
        }).appendTo($svgContainer);

        data.links.forEach(link => {
            const sourceNode = data.nodes.find(n => n.id === link.source.node);
            const targetNode = data.nodes.find(n => n.id === link.target.node);

            if (!sourceNode || !targetNode) {
                console.error('Invalid link:', link);
                return;
            }

            const sourceElement = sourceNode.expanded
                ? $(sourceNode.element).find('.node-columns li').filter(function() { return $(this).text() === link.source.column; })[0]
                : $(sourceNode.element).find('.node-title')[0];

            const targetElement = targetNode.expanded
                ? $(targetNode.element).find('.node-columns li').filter(function() { return $(this).text() === link.target.column; })[0]
                : $(targetNode.element).find('.node-title')[0];

            if (!sourceElement || !targetElement) {
                console.error('Invalid source/target element for link:', link);
                return;
            }

            const sourcePos = getElementCenter(sourceElement);
            const targetPos = getElementCenter(targetElement);

            const pathData = generatePathData(sourcePos, targetPos);

            $svg.append($('<path>').attr({
                d: pathData,
                stroke: 'black',
                fill: 'none'
            }));
        });
    }

    function getElementCenter(element) {
        const $el = $(element);
        const offset = $el.offset();
        return {
            x: offset.left + $el.outerWidth() / 2,
            y: offset.top + $el.outerHeight() / 2
        };
    }

    function generatePathData(source, target) {
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dr = Math.sqrt(dx * dx + dy * dy);
        return `M${source.x},${source.y}A${dr},${dr} 0 0,1 ${target.x},${target.y}`;
    }

    function highlightLinks(nodeId, column, data, nodesMap) {
        const links = data.links.filter(link => link.source.node === nodeId && link.source.column === column);

        $('path').removeClass('line-highlight');

        links.forEach(link => {
            const sourceNode = nodesMap.get(link.source.node);
            const targetNode = nodesMap.get(link.target.node);
            const sourceElement = sourceNode.expanded
                ? $(sourceNode.element).find('.node-columns li').filter(function() { return $(this).text() === link.source.column; })[0]
                : $(sourceNode.element).find('.node-title')[0];
            const targetElement = targetNode.expanded
                ? $(targetNode.element).find('.node-columns li').filter(function() { return $(this).text() === link.target.column; })[0]
                : $(targetNode.element).find('.node-title')[0];
            const sourcePos = getElementCenter(sourceElement);
            const targetPos = getElementCenter(targetElement);
            const pathData = generatePathData(sourcePos, targetPos);
            $('svg').append($('<path>').attr({
                d: pathData,
                stroke: 'orange',
                fill: 'none',
                'class': 'line-highlight'
            }));
        });
    }

    function centerLineage() {
        const $container = $('#lineage-container');
        $container.scrollLeft(($container[0].scrollWidth - $container.width()) / 2);
        $container.scrollTop(($container[0].scrollHeight - $container.height()) / 2);
    }

    $('#expand-all').on('click', function() {
        window.currentData.nodes.forEach(node => node.expanded = true);
        createNodesAndLinks(window.currentData);
    });

    $('#collapse-all').on('click', function() {
        window.currentData.nodes.forEach(node => node.expanded = false);
        createNodesAndLinks(window.currentData);
    });

    fetchDataAndInitialize();
});
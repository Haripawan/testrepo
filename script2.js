document.addEventListener('DOMContentLoaded', () => {
    // Example data for tables and linkages
    const data = {
        tables: [
            {
                tableName: 'raw_product_data',
                database: 'PostgreSQL',
                columns: ['created_at', 'product_id', 'product_name', 'product_description', 'product_category', 'product_brand', 'product_price', 'product_inventory', 'product_weight'],
                popularity: 'Low'
            },
            {
                tableName: 'stg_product',
                database: 'Snowflake',
                columns: ['id', 'name', 'price', 'created_at', 'updated_at', 'category', 'price', 'cost', 'inventory', 'weight', 'isbn'],
                popularity: 'Medium'
            },
            // Add more tables as needed
        ],
        linkages: [
            {
                fromTable: 'raw_product_data',
                fromColumn: 'product_name',
                toTable: 'stg_product',
                toColumn: 'name'
            }
            // Add more linkages as needed
        ]
    };

    // Function to create a lineage node
    function createLineageNode(tableData, index) {
        // Create the node container
        const node = document.createElement('div');
        node.className = 'node';
        node.id = `node-${index}`;
        node.style.left = '50%';
        node.style.top = '50%';
        node.style.transform = 'translate(-50%, -50%)';
        node.draggable = true;

        // Create the node title
        const title = document.createElement('div');
        title.className = 'node-title';
        title.innerHTML = `
            ${tableData.tableName}
            <span>${tableData.database}</span>
            <span class="icon">&#9662;</span>
        `;
        node.appendChild(title);

        // Create the separator line
        const separator = document.createElement('div');
        separator.className = 'separator';
        node.appendChild(separator);

        // Create the list of columns
        const columnsList = document.createElement('ul');
        columnsList.className = 'node-columns';
        tableData.columns.forEach((column, columnIndex) => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <span>${column}</span>
                <span class="icon">&#9679;</span>
            `;
            listItem.id = `node-${index}-column-${columnIndex}`;
            listItem.dataset.columnName = column; // Store column name in dataset
            columnsList.appendChild(listItem);
        });
        node.appendChild(columnsList);

        // Add click event to the title to toggle visibility of columns
        title.addEventListener('click', () => {
            if (columnsList.style.display === 'none' || columnsList.style.display === '') {
                columnsList.style.display = 'block';
                title.querySelector('.icon').innerHTML = '&#9652;'; // Up arrow
            } else {
                columnsList.style.display = 'none';
                title.querySelector('.icon').innerHTML = '&#9662;'; // Down arrow
            }
        });

        // Add drag event listeners to the node
        node.addEventListener('dragstart', dragStart);
        node.addEventListener('dragend', dragEnd);

        return node;
    }

    // Function to draw a line between two elements
    function drawLine(startElement, endElement) {
        const svg = document.getElementById('svgContainer');
        const startRect = startElement.getBoundingClientRect();
        const endRect = endElement.getBoundingClientRect();

        const startX = startRect.right + window.scrollX;
        const startY = startRect.top + window.scrollY + (startRect.height / 2);
        const endX = endRect.left + window.scrollX;
        const endY = endRect.top + window.scrollY + (endRect.height / 2);

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', startX);
        line.setAttribute('y1', startY);
        line.setAttribute('x2', endX);
        line.setAttribute('y2', endY);
        line.setAttribute('stroke', 'black');
        line.setAttribute('stroke-width', '2');

        svg.appendChild(line);
    }

    // Get the container for lineage nodes
    const lineageContainer = document.getElementById('lineage-container');

    // Create and add lineage nodes to the container
    data.tables.forEach((tableData, index) => {
        const lineageNode = createLineageNode(tableData, index);
        lineageContainer.appendChild(lineageNode);
    });

    // Draw the linkages
    data.linkages.forEach(linkage => {
        const fromTableIndex = data.tables.findIndex(table => table.tableName === linkage.fromTable);
        const toTableIndex = data.tables.findIndex(table => table.tableName === linkage.toTable);

        if (fromTableIndex !== -1 && toTableIndex !== -1) {
            const fromColumnIndex = data.tables[fromTableIndex].columns.findIndex(column => column === linkage.fromColumn);
            const toColumnIndex = data.tables[toTableIndex].columns.findIndex(column => column === linkage.toColumn);

            if (fromColumnIndex !== -1 && toColumnIndex !== -1) {
                const fromColumnElement = document.getElementById(`node-${fromTableIndex}-column-${fromColumnIndex}`);
                const toColumnElement = document.getElementById(`node-${toTableIndex}-column-${toColumnIndex}`);

                drawLine(fromColumnElement, toColumnElement);
            }
        }
    });

    // Drag functions
    let dragSrcEl = null;

    function dragStart(e) {
        dragSrcEl = this;
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', this.innerHTML);
        this.style.opacity = '0.4';
    }

    function dragEnd(e) {
        this.style.opacity = '1.0';
        const svg = document.getElementById('svgContainer');
        while (svg.firstChild) {
            svg.removeChild(svg.firstChild);
        }
        data.linkages.forEach(linkage => {
            const fromTableIndex = data.tables.findIndex(table => table.tableName === linkage.fromTable);
            const toTableIndex = data.tables.findIndex(table => table.tableName === linkage.toTable);

            if (fromTableIndex !== -1 && toTableIndex !== -1) {
                const fromColumnIndex = data.tables[fromTableIndex].columns.findIndex(column => column === linkage.fromColumn);
                const toColumnIndex = data.tables[toTableIndex].columns.findIndex(column => column === linkage.toColumn);

                if (fromColumnIndex !== -1 && toColumnIndex !== -1) {
                    const fromColumnElement = document.getElementById(`node-${fromTableIndex}-column-${fromColumnIndex}`);
                    const toColumnElement = document.getElementById(`node-${toTableIndex}-column-${toColumnIndex}`);

                    draw
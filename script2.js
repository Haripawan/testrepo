document.addEventListener('DOMContentLoaded', () => {
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
            }
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

    const lineageContainer = document.getElementById('lineage-container');

    function createLineageNode(tableData, index) {
        const node = document.createElement('div');
        node.className = 'node';
        node.id = `node-${index}`;
        node.draggable = true;

        const title = document.createElement('div');
        title.className = 'node-title';
        title.innerHTML = `${tableData.tableName} <span>${tableData.database}</span>`;
        node.appendChild(title);

        const separator = document.createElement('div');
        separator.className = 'separator';
        node.appendChild(separator);

        const columnsList = document.createElement('ul');
        columnsList.className = 'node-columns';
        tableData.columns.forEach((column, columnIndex) => {
            const listItem = document.createElement('li');
            listItem.innerHTML = column;
            listItem.id = `node-${index}-column-${columnIndex}`;
            listItem.dataset.columnName = column;
            columnsList.appendChild(listItem);
        });
        node.appendChild(columnsList);

        title.addEventListener('click', () => {
            if (columnsList.style.display === 'none' || columnsList.style.display === '') {
                columnsList.style.display = 'block';
            } else {
                columnsList.style.display = 'none';
            }
            updateLines();
        });

        node.addEventListener('dragstart', dragStart);
        node.addEventListener('dragend', dragEnd);

        return node;
    }

    function drawLink(startElement, endElement) {
        const svg = d3.select('#svgContainer');
        const startRect = startElement.getBoundingClientRect();
        const endRect = endElement.getBoundingClientRect();

        const startX = startRect.right + window.scrollX;
        const startY = startRect.top + window.scrollY + (startRect.height / 2);
        const endX = endRect.left + window.scrollX;
        const endY = endRect.top + window.scrollY + (endRect.height / 2);

        svg.append('path')
            .attr('d', `M${startX},${startY} C${(startX + endX) / 2},${startY} ${(startX + endX) / 2},${endY} ${endX},${endY}`)
            .attr('stroke', 'black')
            .attr('fill', 'none');
    }

    data.tables.forEach((tableData, index) => {
        const lineageNode = createLineageNode(tableData, index);
        lineageContainer.appendChild(lineageNode);
    });

    function updateLines() {
        const svg = d3.select('#svgContainer');
        svg.selectAll('*').remove();

        data.linkages.forEach(linkage => {
            const fromTableIndex = data.tables.findIndex(table => table.tableName === linkage.fromTable);
            const toTableIndex = data.tables.findIndex(table => table.tableName === linkage.toTable);

            if (fromTableIndex !== -1 && toTableIndex !== -1) {
                const fromColumnIndex = data.tables[fromTableIndex].columns.findIndex(column => column === linkage.fromColumn);
                const toColumnIndex = data.tables[toTableIndex].columns.findIndex(column => column === linkage.toColumn);

                const fromElement = document.getElementById(`node-${fromTableIndex}`);
                const toElement = document.getElementById(`node-${toTableIndex}`);

                const fromColumnElement = document.getElementById(`node-${fromTableIndex}-column-${fromColumnIndex}`);
                const toColumnElement = document.getElementById(`node-${toTableIndex}-column-${toColumnIndex}`);

                const fromElementToUse = fromColumnElement.style.display === 'block' ? fromColumnElement : fromElement.querySelector('.node-title');
                const toElementToUse = toColumnElement.style.display === 'block' ? toColumnElement : toElement.querySelector('.node-title');

                drawLink(fromElementToUse, toElementToUse);
            }
        });
    }

    let dragSrcEl = null;
    let offsetX, offsetY;

    function dragStart(e) {
        dragSrcEl = this;
        const rect = this.getBoundingClientRect();
        offsetX = e.clientX - rect.left;
        offsetY = e.clientY - rect.top;
        e.dataTransfer.setData('text/plain', ''); // Required for Firefox
        this.style.opacity = '0.4';
    }

    function dragEnd(e) {
        this.style.opacity = '1.0';
        const newX = e.clientX - offsetX;
        const newY = e.clientY - offsetY;
        this.style.left = `${newX}px`;
        this.style.top = `${newY}px`;
        updateLines();
    }

    document.querySelectorAll('.node').forEach(node => {
        node.addEventListener('dragstart', dragStart);
        node.addEventListener('dragend', dragEnd);
    });

    updateLines();
});

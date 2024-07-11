document.addEventListener('DOMContentLoaded', () => {
    // Example data for tables
    const tablesData = [
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
    ];

    // Function to create a lineage node
    function createLineageNode(tableData) {
        // Create the node container
        const node = document.createElement('div');
        node.className = 'node';

        // Create the node title
        const title = document.createElement('div');
        title.className = 'node-title';
        title.innerHTML = `
            ${tableData.tableName}
            <span>${tableData.database}</span>
            <span class="icon">&#9662;</span>
        `;
        node.appendChild(title);

        // Create the list of columns
        const columnsList = document.createElement('ul');
        columnsList.className = 'node-columns';
        tableData.columns.forEach(column => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <span>${column}</span>
                <span class="icon">&#9679;</span>
            `;
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

        return node;
    }

    // Get the container for lineage nodes
    const lineageContainer = document.getElementById('lineage-container');

    // Create and add lineage nodes to the container
    tablesData.forEach(tableData => {
        const lineageNode = createLineageNode(tableData);
        lineageContainer.appendChild(lineageNode);
    });
});
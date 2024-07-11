document.addEventListener('DOMContentLoaded', () => {
    // Example data for a table
    const tableData = {
        tableName: 'Users',
        columns: ['id', 'name', 'email', 'created_at', 'updated_at']
    };

    // Function to create a lineage node
    function createLineageNode(tableData) {
        // Create the node container
        const node = document.createElement('div');
        node.className = 'node';

        // Create the node title
        const title = document.createElement('div');
        title.className = 'node-title';
        title.textContent = tableData.tableName;
        node.appendChild(title);

        // Create the list of columns
        const columnsList = document.createElement('ul');
        columnsList.className = 'node-columns';
        tableData.columns.forEach(column => {
            const listItem = document.createElement('li');
            listItem.textContent = column;
            columnsList.appendChild(listItem);
        });
        node.appendChild(columnsList);

        // Add click event to the title to toggle visibility of columns
        title.addEventListener('click', () => {
            if (columnsList.style.display === 'none' || columnsList.style.display === '') {
                columnsList.style.display = 'block';
            } else {
                columnsList.style.display = 'none';
            }
        });

        return node;
    }

    // Get the container for lineage nodes
    const lineageContainer = document.getElementById('lineage-container');

    // Create a lineage node and add it to the container
    const lineageNode = createLineageNode(tableData);
    lineageContainer.appendChild(lineageNode);
});
SELECT 
    ID,
    Month,
    Sales
FROM 
    sales_data
UNPIVOT (
    Sales FOR Month IN (Jan AS 'Jan', Feb AS 'Feb', Mar AS 'Mar')
);
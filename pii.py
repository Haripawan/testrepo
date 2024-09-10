import cx_Oracle
import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Function to fetch the first 500 records from a table
def fetch_records(connection, table_name):
    query = f"SELECT * FROM {table_name} FETCH FIRST 500 ROWS ONLY"
    try:
        # Fetch the data into a pandas DataFrame
        data = pd.read_sql(query, connection)
        return data
    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()

# Function to analyze PII in a table's data
def analyze_pii(data):
    analyzer = AnalyzerEngine()
    sensitive_columns = set()

    # Iterate over columns and check for PII
    for column in data.columns:
        # Combine rows into one text block to run Presidio analysis
        combined_text = ' '.join(data[column].astype(str).values)

        # Analyze the column's text
        results = analyzer.analyze(text=combined_text, entities=[], language='en')

        # If any PII is detected, mark this column as sensitive
        if results:
            sensitive_columns.add(column)
    
    return sensitive_columns

# Function to generate the report
def generate_report(connection, tables):
    report = []
    for table_name in tables:
        print(f"Analyzing table: {table_name}")
        # Fetch first 500 records from the table
        data = fetch_records(connection, table_name)

        if not data.empty:
            # Analyze the data for PII
            sensitive_columns = analyze_pii(data)

            if sensitive_columns:
                report.append({
                    'table': table_name,
                    'sensitive_columns': ', '.join(sensitive_columns)
                })
        else:
            print(f"No data found for table: {table_name}")

    return report

# Function to fetch all tables from the database
def fetch_all_tables(connection):
    query = "SELECT table_name FROM user_tables"
    cursor = connection.cursor()
    cursor.execute(query)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables

# Function to write the report to a file
def write_report_to_file(report, filename='pii_report.csv'):
    report_df = pd.DataFrame(report)
    report_df.to_csv(filename, index=False)
    print(f"Report saved to {filename}")

# Main function to connect to Oracle, analyze tables, and generate the report
def main():
    # Connect to Oracle database
    dsn_tns = cx_Oracle.makedsn('host', 'port', service_name='your_service_name')
    connection = cx_Oracle.connect(user='your_username', password='your_password', dsn=dsn_tns)

    try:
        # Fetch all tables from the schema
        tables = fetch_all_tables(connection)

        # Generate the report by analyzing PII in each table
        report = generate_report(connection, tables)

        # Write the report to a CSV file
        write_report_to_file(report)
    
    finally:
        # Close the database connection
        connection.close()

if __name__ == "__main__":
    main()
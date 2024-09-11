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
    
##################################
import cx_Oracle
import pandas as pd
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, EntityRecognizer
from presidio_analyzer.nlp_engine import SpacyNlpEngine
import spacy  # Import spaCy

# Load the installed spaCy model
nlp_model = spacy.load("en_core_web_lg")  # or "en_core_web_sm" depending on what you installed

# Set up Presidio's NLP engine to use the spaCy model
nlp_engine = SpacyNlpEngine({"en": "en_core_web_lg"})  # Specify the spaCy model to use
registry = RecognizerRegistry()  # Create a recognizer registry
registry.load_predefined_recognizers()  # Load built-in recognizers

# Set up Presidio analyzer engine with the spaCy NLP engine
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)

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
    sensitive_columns = set()

    # Iterate over columns and check for PII
    for column in data.columns:
        # Combine rows into one text block to run Presidio analysis
        combined_text = ' '.join(data[column].astype(str).values)

        # Analyze the column's text using Presidio with spaCy engine
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
    
    
##########################

import cx_Oracle
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import SpacyNlpEngine
import pandas as pd

# Step 1: Connect to Oracle Database
dsn_tns = cx_Oracle.makedsn('hostname', 'port', service_name='service_name')
connection = cx_Oracle.connect(user='username', password='password', dsn=dsn_tns)
cursor = connection.cursor()

# Step 2: Setup Presidio Analyzer
nlp_engine = SpacyNlpEngine()  # Default to spacy engine
registry = RecognizerRegistry()
registry.load_predefined_recognizers()
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)

# Step 3: Fetch Data from Oracle
query = "SELECT * FROM your_table_name FETCH FIRST 500 ROWS ONLY"
cursor.execute(query)
data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

# Step 4: Analyze for PII and generate a detailed report
def analyze_pii(dataframe, table_name):
    pii_report = []
    
    for column in dataframe.columns:
        for value in dataframe[column].astype(str):
            results = analyzer.analyze(text=value, entities=[], language='en')
            
            # If PII is detected, store it in the report
            for result in results:
                pii_report.append({
                    "Table": table_name,
                    "Column": column,
                    "Detected PII Type": result.entity_type,  # The type of PII (e.g., EMAIL, PHONE_NUMBER, etc.)
                    "Confidence Score": result.score,         # Confidence score for the detection
                    "Sample Value": value                     # Optional: store the sample value for context (useful for validation)
                })
    
    return pii_report

# Step 5: Generate Report for Multiple Tables
def generate_report(tables):
    all_pii_reports = []
    
    for table in tables:
        # Fetch the first 500 rows for each table
        query = f"SELECT * FROM {table} FETCH FIRST 500 ROWS ONLY"
        cursor.execute(query)
        data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        
        # Analyze PII in the table and append results
        table_pii_report = analyze_pii(data, table)
        all_pii_reports.extend(table_pii_report)
    
    return all_pii_reports

# List of tables to scan
tables = ["your_table_name1", "your_table_name2", "your_table_name3"]

# Generate PII report
pii_reports = generate_report(tables)

# Convert the PII report into a pandas DataFrame for easier viewing and exporting
pii_report_df = pd.DataFrame(pii_reports)

# Step 6: Print or Export the Report
print(pii_report_df)

# Optional: Export to CSV
pii_report_df.to_csv("pii_report.csv", index=False)

#########################

import os
import cx_Oracle
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import SpacyNlpEngine
import pandas as pd
import spacy
from collections import defaultdict

# Step 1: Connect to Oracle Database
dsn_tns = cx_Oracle.makedsn('hostname', 'port', service_name='service_name')
connection = cx_Oracle.connect(user='username', password='password', dsn=dsn_tns)
cursor = connection.cursor()

# Step 2: Load the spaCy model from the local installation
# Assuming the model is installed locally, adjust the path if necessary.
spacy_model_path = "en_core_web_lg"  # Ensure the model is installed offline and accessible
nlp = spacy.load(spacy_model_path)

# Step 3: Set up the Presidio analyzer to use the local spaCy NLP engine
nlp_engine = SpacyNlpEngine(spacy_model=nlp)  # Provide the locally loaded spaCy model
registry = RecognizerRegistry()
registry.load_predefined_recognizers()  # Load recognizers
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)

# Step 4: Fetch Data from Oracle
query = "SELECT * FROM your_table_name FETCH FIRST 500 ROWS ONLY"
cursor.execute(query)
data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

# Step 5: Analyze for PII and calculate average confidence per column
def analyze_pii(dataframe, table_name):
    pii_report = []

    for column in dataframe.columns:
        # Dictionary to hold confidence scores for each detected PII type
        pii_scores = defaultdict(list)  # {PII_type: [list of confidence scores]}
        
        for value in dataframe[column].astype(str):
            results = analyzer.analyze(text=value, entities=[], language='en')
            
            # Store the confidence score for each PII type detected in the column
            for result in results:
                pii_scores[result.entity_type].append(result.score)

        # If any PII was detected in this column, compute the average confidence for each PII type
        if pii_scores:
            avg_confidences = {pii_type: sum(scores) / len(scores) for pii_type, scores in pii_scores.items()}
            # Get the PII type with the highest average confidence
            best_pii_type = max(avg_confidences, key=avg_confidences.get)
            best_avg_confidence = avg_confidences[best_pii_type]
            
            # Append the result to the report
            pii_report.append({
                "Table": table_name,
                "Column": column,
                "Detected PII Type": best_pii_type,
                "Average Confidence Score": best_avg_confidence
            })

    return pii_report

# Step 6: Generate Report for Multiple Tables
def generate_report(tables):
    all_pii_reports = []
    
    for table in tables:
        # Fetch the first 500 rows for each table
        query = f"SELECT * FROM {table} FETCH FIRST 500 ROWS ONLY"
        cursor.execute(query)
        data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        
        # Analyze PII in the table and append results
        table_pii_report = analyze_pii(data, table)
        all_pii_reports.extend(table_pii_report)
    
    return all_pii_reports

# List of tables to scan
tables = ["your_table_name1", "your_table_name2", "your_table_name3"]

# Generate PII report
pii_reports = generate_report(tables)

# Convert the PII report into a pandas DataFrame for easier viewing and exporting
pii_report_df = pd.DataFrame(pii_reports)

# Step 7: Print or Export the Report
print(pii_report_df)

# Optional: Export to CSV
pii_report_df.to_csv("pii_report.csv", index=False)
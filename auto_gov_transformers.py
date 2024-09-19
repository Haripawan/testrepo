import os
import cx_Oracle
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer.recognizer_registry import RecognizerRegistry
import pandas as pd
import spacy
import json
from transformers import pipeline

# Step 1: Load configurations from files
def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

# Load database connection config
db_config = load_config("connection_config.json")

# Load custom PII patterns config
pii_config = load_config("pii_patterns_config.json")

# Step 2: Connect to Oracle Database using config file
dsn_tns = cx_Oracle.makedsn(db_config["hostname"], db_config["port"], service_name=db_config["service_name"])
connection = cx_Oracle.connect(user=db_config["username"], password=db_config["password"], dsn=dsn_tns)
cursor = connection.cursor()

# Step 3: Load the spaCy model from the local installation
spacy_model_path = "en_core_web_lg"  # Ensure the model is installed offline and accessible
nlp = spacy.load(spacy_model_path)

# Step 4: Set up the Presidio analyzer to use the local spaCy NLP engine
nlp_engine = SpacyNlpEngine(spacy_model=spacy_model_path)
registry = RecognizerRegistry()
registry.load_predefined_recognizers()  # Load predefined recognizers
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)

# Step 5: Set up the Transformer-based NER model
class TransformersNlpEngine:
    def __init__(self, model_name="dbmdz/bert-large-cased-finetuned-conll03-english"):
        # Load Hugging Face NER model
        self.nlp = pipeline("ner", model=model_name, grouped_entities=True)

    def analyze(self, text, language=None):
        # Run NER using Hugging Face transformer model
        results = self.nlp(text)
        entities = []
        for result in results:
            entity = RecognizerResult(
                entity_type=result['entity_group'],  # Use the entity group/type
                start=result['start'],
                end=result['end'],
                score=result['score']
            )
            entities.append(entity)
        return entities

# Instantiate the Transformer NLP engine
transformers_nlp_engine = TransformersNlpEngine()

# Step 6: Add custom PII patterns from configuration
def add_custom_patterns(analyzer, pii_config):
    for pattern_data in pii_config["custom_pii_patterns"]:
        pattern = Pattern(name=pattern_data["name"], regex=pattern_data["regex"], score=pattern_data["confidence"])
        recognizer = PatternRecognizer(supported_entity=pattern_data["pii_type"], patterns=[pattern])
        analyzer.registry.add_recognizer(recognizer)

# Add custom patterns to the analyzer
add_custom_patterns(analyzer, pii_config)

# Step 7: Get list of custom PII types from the config
custom_pii_types = [pattern_data['pii_type'] for pattern_data in pii_config["custom_pii_patterns"]]

# Step 8: Fetch Data from Oracle (Main Table and Column Definitions Table)
query = "SELECT * FROM your_table_name FETCH FIRST 500 ROWS ONLY"
cursor.execute(query)
data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

# Fetch column definitions from the definitions table
query_definitions = "SELECT * FROM column_definitions_table"
cursor.execute(query_definitions)
column_definitions = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

# Step 9: Analyze for PII, considering both column definitions and data content
def analyze_pii(dataframe, definitions_df, table_name):
    pii_report = []

    # Filter out columns that have '_ID', '_CD', or '_DT' in the name
    columns_to_analyze = [col for col in dataframe.columns if not (col.endswith('_ID') or col.endswith('_CD') or col.endswith('_DT'))]

    for column in columns_to_analyze:
        # Variables to track the highest confidence scores and sample values for default, custom, and transformer-based PII types
        max_default_pii_type = None
        max_default_confidence = 0
        default_sample_value = None

        max_custom_pii_type = None
        max_custom_confidence = 0
        custom_sample_value = None

        max_transformer_pii_type = None
        max_transformer_confidence = 0
        transformer_sample_value = None

        # Get the column definition/context from the definitions table
        column_definition = definitions_df[definitions_df['COLUMN_NAME'] == column].iloc[0]
        column_context = column_definition['COLUMN_DEFINITION'] if 'COLUMN_DEFINITION' in column_definition else "Unknown"

        # Now analyze the actual content of the column
        for value in dataframe[column].astype(str):
            # Run default analysis (with spaCy and custom recognizers)
            default_results = analyzer.analyze(text=value, entities=[], language='en')

            # Separate default and custom recognizers based on entity_type
            for result in default_results:
                # Custom recognizer match
                if result.entity_type in custom_pii_types:
                    if result.score > max_custom_confidence:
                        max_custom_confidence = result.score
                        max_custom_pii_type = result.entity_type
                        custom_sample_value = value
                else:
                    if result.score > max_default_confidence:
                        max_default_confidence = result.score
                        max_default_pii_type = result.entity_type
                        default_sample_value = value

            # Run transformer-based analysis
            transformer_results = transformers_nlp_engine.analyze(text=value)
            for result in transformer_results:
                if result.score > max_transformer_confidence:
                    max_transformer_confidence = result.score
                    max_transformer_pii_type = result.entity_type
                    transformer_sample_value = value

        # Append the result to the report with column context
        pii_report.append({
            "Table": table_name,
            "Column": column,
            "Column Definition": column_context,
            "Default PII Type": max_default_pii_type,
            "Default PII Confidence": max_default_confidence,
            "Default Sample Value": default_sample_value,
            "Custom PII Type": max_custom_pii_type,
            "Custom PII Confidence": max_custom_confidence,
            "Custom Sample Value": custom_sample_value,
            "Transformer PII Type": max_transformer_pii_type,
            "Transformer PII Confidence": max_transformer_confidence,
            "Transformer Sample Value": transformer_sample_value,
        })

    return pii_report

# Step 10: Generate Report for Multiple Tables
def generate_report(tables):
    all_pii_reports = []

    for table in tables:
        # Fetch the first 500 rows for each table
        query = f"SELECT * FROM {table} FETCH FIRST 500 ROWS ONLY"
        cursor.execute(query)
        data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

        # Analyze PII in the table and append results
        table_pii_report = analyze_pii(data, column_definitions, table)
        all_pii_reports.extend(table_pii_report)

    return all_pii_reports

# List of tables to scan
tables = ["your_table_name1", "your_table_name2", "your_table_name3"]

# Generate PII report
pii_reports = generate_report(tables)

# Convert the PII report into a pandas DataFrame for easier viewing and exporting
pii_report_df = pd.DataFrame(pii_reports)

# Step 11: Convert all columns to string to avoid scientific notation in Excel/CSV
pii_report_df = pii_report_df.astype(str)

# Step 12: Export the report to CSV
pii_report_df.to_csv("pii_report_with_transformers.csv", index=False)
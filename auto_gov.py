import os
import cx_Oracle
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer.recognizer_registry import RecognizerRegistry
import pandas as pd
import spacy
from collections import defaultdict
import json

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
nlp_engine = SpacyNlpEngine(spacy_model=nlp)
registry = RecognizerRegistry()
registry.load_predefined_recognizers()  # Load predefined recognizers
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)

# Step 5: Add custom PII patterns from configuration
def add_custom_patterns(analyzer, pii_config):
    for pattern_data in pii_config["custom_pii_patterns"]:
        pattern = Pattern(name=pattern_data["name"], regex=pattern_data["regex"], score=pattern_data["confidence"])
        recognizer = PatternRecognizer(supported_entity=pattern_data["pii_type"], patterns=[pattern])
        analyzer.registry.add_recognizer(recognizer)

# Add custom patterns to the analyzer
add_custom_patterns(analyzer, pii_config)

# Step 6: Fetch Data from Oracle
query = "SELECT * FROM your_table_name FETCH FIRST 500 ROWS ONLY"
cursor.execute(query)
data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

# Step 7: Analyze for PII, separate default and custom results, and add sample values
def analyze_pii(dataframe, table_name):
    pii_report = []

    for column in dataframe.columns:
        # Dictionaries to hold confidence scores and sample values for default and custom PII types
        default_pii_scores = defaultdict(list)  # {PII_type: [list of confidence scores]} for default recognizers
        custom_pii_scores = defaultdict(list)  # {PII_type: [list of confidence scores]} for custom patterns
        default_pii_samples = {}  # {PII_type: sample_value} for default PII types
        custom_pii_samples = {}  # {PII_type: sample_value} for custom PII types

        for value in dataframe[column].astype(str):
            results = analyzer.analyze(text=value, entities=[], language='en')

            # Separate default and custom recognizers
            for result in results:
                if result.recognizer_name.startswith("PatternRecognizer"):
                    # Custom recognizer
                    custom_pii_scores[result.entity_type].append(result.score)
                    if result.entity_type not in custom_pii_samples:
                        custom_pii_samples[result.entity_type] = value
                else:
                    # Default recognizer
                    default_pii_scores[result.entity_type].append(result.score)
                    if result.entity_type not in default_pii_samples:
                        default_pii_samples[result.entity_type] = value

        # If any default PII was detected in this column, compute the average confidence for default recognizers
        if default_pii_scores:
            default_avg_confidences = {pii_type: sum(scores) / len(scores) for pii_type, scores in default_pii_scores.items()}
            best_default_pii_type = max(default_avg_confidences, key=default_avg_confidences.get)
            best_default_avg_confidence = default_avg_confidences[best_default_pii_type]
            default_sample_value = default_pii_samples[best_default_pii_type]
        else:
            best_default_pii_type = None
            best_default_avg_confidence = None
            default_sample_value = None

        # If any custom PII was detected in this column, compute the average confidence for custom patterns
        if custom_pii_scores:
            custom_avg_confidences = {pii_type: sum(scores) / len(scores) for pii_type, scores in custom_pii_scores.items()}
            best_custom_pii_type = max(custom_avg_confidences, key=custom_avg_confidences.get)
            best_custom_avg_confidence = custom_avg_confidences[best_custom_pii_type]
            custom_sample_value = custom_pii_samples[best_custom_pii_type]
        else:
            best_custom_pii_type = None
            best_custom_avg_confidence = None
            custom_sample_value = None

        # Append the result to the report
        pii_report.append({
            "Table": table_name,
            "Column": column,
            "Default PII Type": best_default_pii_type,
            "Default PII Confidence": best_default_avg_confidence,
            "Default Sample Value": default_sample_value,
            "Custom PII Type": best_custom_pii_type,
            "Custom PII Confidence": best_custom_avg_confidence,
            "Custom Sample Value": custom_sample_value
        })

    return pii_report

# Step 8: Generate Report for Multiple Tables
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

# Step 9: Print or Export the Report
print(pii_report_df)

# Optional: Export to CSV
pii_report_df.to_csv("pii_report.csv", index=False)


'''{
  "hostname": "your_hostname",
  "port": "1521",
  "service_name": "your_service_name",
  "username": "your_username",
  "password": "your_password"
}'''


'''{
  "custom_pii_patterns": [
    {
      "name": "CUSTOM_SSN",
      "regex": "\\b\\d{3}-\\d{2}-\\d{4}\\b",
      "pii_type": "US_SOCIAL_SECURITY",
      "confidence": 0.9
    },
    {
      "name": "CUSTOM_CREDIT_CARD",
      "regex": "\\b(?:\\d[ -]*?){13,16}\\b",
      "pii_type": "CREDIT_CARD",
      "confidence": 0.95
    }
  ]
}'''
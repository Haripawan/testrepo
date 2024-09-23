import tkinter as tk
from tkinter import ttk
import cx_Oracle
import pandas as pd

# Connect to the Oracle Database
def get_oracle_columns(schema_name, table_name):
    connection = cx_Oracle.connect('your_username/your_password@your_host:your_port/your_service_name')
    cursor = connection.cursor()
    
    # Query ALL_TAB_COLUMNS to get column data for a given table
    query = f"""
        SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH 
        FROM ALL_TAB_COLUMNS 
        WHERE OWNER = '{schema_name.upper()}' AND TABLE_NAME = '{table_name.upper()}'
        ORDER BY COLUMN_ID
    """
    
    cursor.execute(query)
    columns = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Returning the column data
    return columns

# Sample function to read from Oracle, replace 'SCHEMA' and 'TABLE'
source_columns = get_oracle_columns('SCHEMA', 'TABLE')

# Create the main window
root = tk.Tk()
root.title("Source-Target Column Mapping")
root.geometry("800x400")

# Define frame for the source and target sections
frame = tk.Frame(root)
frame.pack(pady=20, padx=20)

# Create the Treeview for Source Section
source_label = tk.Label(frame, text="Source Columns", font=("Arial", 12, "bold"))
source_label.grid(row=0, column=0, padx=10, pady=10)

# Create the Treeview for displaying source columns
source_tree = ttk.Treeview(frame, columns=("column_name", "data_type", "data_length"), show="headings", height=10)
source_tree.heading("column_name", text="Column Name")
source_tree.heading("data_type", text="Data Type")
source_tree.heading("data_length", text="Data Length")
source_tree.column("column_name", width=150)
source_tree.column("data_type", width=100)
source_tree.column("data_length", width=100)

# Add the source data to the Treeview
for column in source_columns:
    source_tree.insert("", tk.END, values=column)

source_tree.grid(row=1, column=0, padx=10, pady=10)

# Create the Target Section
target_label = tk.Label(frame, text="Target Columns (Editable)", font=("Arial", 12, "bold"))
target_label.grid(row=0, column=1, padx=10, pady=10)

# Create a list to store target entries
target_entries = []

# Function to update the source-target mapping
def update_mapping():
    mapping_data = []
    
    # Loop through source columns and corresponding target entries
    for i, column in enumerate(source_columns):
        source_column_name = column[0]
        target_column_name = target_entries[i].get()
        
        # Append to mapping data
        mapping_data.append({
            "source_column": source_column_name,
            "target_column": target_column_name,
            "data_type": column[1],  # Optionally, keep data type from source
            "data_length": column[2] # Optionally, keep data length from source
        })
    
    # Convert to DataFrame
    mapping_df = pd.DataFrame(mapping_data)
    
    # Save the mapping specification to a CSV file
    mapping_df.to_csv('mapping_spec.csv', index=False)
    
    # Show a message or print confirmation
    print("Mapping specification saved to 'mapping_spec.csv'")

# Populate the target section with editable entries
for i, column in enumerate(source_columns):
    # Create an Entry for each target column
    target_entry = tk.Entry(frame)
    target_entry.grid(row=i+1, column=1, padx=10, pady=5)
    target_entries.append(target_entry)

# Button to trigger update and save the mapping specification
save_button = tk.Button(root, text="Save Mapping Specification", command=update_mapping)
save_button.pack(pady=20)

# Run the Tkinter main loop
root.mainloop()
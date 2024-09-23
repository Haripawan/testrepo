import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import pandas as pd

# Create the main window
root = tk.Tk()
root.title("Table Mapping Application")
root.geometry("800x600")

# Create a notebook (tab system)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# --- Create Frames for each Tab ---
info_tab = ttk.Frame(notebook)
layout_tab = ttk.Frame(notebook)
mapping_tab = ttk.Frame(notebook)  # Will add functionality here
column_list_tab = ttk.Frame(notebook)

# Add tabs to the notebook
notebook.add(info_tab, text="Info")
notebook.add(layout_tab, text="Layout")
notebook.add(mapping_tab, text="Mapping")
notebook.add(column_list_tab, text="Column List")

# --------- Functionality for the Mapping Tab ---------

# Frame for the table creation and mapping functionality in the "Mapping" tab
frame = tk.Frame(mapping_tab)
frame.pack(pady=20, padx=20)

# Label for Table Name
table_name_label = tk.Label(frame, text="Target Table Name:", font=("Arial", 12))
table_name_label.grid(row=0, column=0, padx=10, pady=10)

# Text field to input the target table name
table_name_entry = tk.Entry(frame, width=30)
table_name_entry.grid(row=0, column=1, padx=10, pady=10)

# Create an empty list to store target column information
target_columns = []
target_column_widgets = []

# Function to map a source column to the target column
def map_source_column(target_index):
    # Prompt user to select a source column from the list
    selected_column = simpledialog.askstring("Map Source Column", "Enter Source Column Name:", parent=root)
    
    if selected_column:
        # Update the target column's mapped source column in the UI
        target_column_widgets[target_index]['mapped_source'].set(selected_column)

# Function to add a new target column
def add_target_column():
    row = len(target_columns) + 1
    
    # Entry for the target column name
    target_column_name = tk.Entry(frame, width=20)
    target_column_name.grid(row=row, column=1, padx=10, pady=5)
    
    # Entry to display the mapped source column (non-editable)
    mapped_source_var = tk.StringVar()
    mapped_source_entry = tk.Entry(frame, textvariable=mapped_source_var, width=20, state="readonly")
    mapped_source_entry.grid(row=row, column=2, padx=10, pady=5)
    
    # Button to map the source column
    map_button = tk.Button(frame, text="Map Source", command=lambda idx=len(target_columns): map_source_column(idx))
    map_button.grid(row=row, column=3, padx=10, pady=5)
    
    # Append the new column info to the list
    target_columns.append({"column_name": "", "mapped_source": ""})
    target_column_widgets.append({
        "target_entry": target_column_name,
        "mapped_source": mapped_source_var
    })

# Function to create the target table spec and save the mapping
def save_mapping():
    table_name = table_name_entry.get()
    
    if not table_name:
        messagebox.showerror("Error", "Please enter the target table name.")
        return
    
    mapping_data = []
    for i, column_info in enumerate(target_columns):
        target_column_name = target_column_widgets[i]['target_entry'].get()
        mapped_source = target_column_widgets[i]['mapped_source'].get()
        
        if not target_column_name:
            messagebox.showerror("Error", f"Please enter the target column name for column {i+1}.")
            return
        
        if not mapped_source:
            messagebox.showerror("Error", f"Please map the source column for target column {target_column_name}.")
            return
        
        mapping_data.append({
            "target_column": target_column_name,
            "mapped_source": mapped_source
        })
    
    # Convert to DataFrame and save to CSV (or any other format you prefer)
    mapping_df = pd.DataFrame(mapping_data)
    mapping_df.to_csv(f"{table_name}_mapping_spec.csv", index=False)
    
    messagebox.showinfo("Success", f"Mapping saved to {table_name}_mapping_spec.csv")

# Button to add a new column
add_column_button = tk.Button(mapping_tab, text="Add Target Column", command=add_target_column)
add_column_button.pack(pady=10)

# Button to save the mapping
save_button = tk.Button(mapping_tab, text="Save Mapping Specification", command=save_mapping)
save_button.pack(pady=10)

# ------- Add a placeholder for the "Save" button at the bottom ------
save_frame = tk.Frame(root)
save_frame.pack(side="bottom", fill="x")

# "Save" button placeholder
save_app_button = tk.Button(save_frame, text="Save", command=save_mapping)
save_app_button.pack(side="left", padx=20, pady=10)

# Add a column on load for demonstration purposes
add_target_column()

# Run the Tkinter main loop
root.mainloop()
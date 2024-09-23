import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

# Create the main window
root = tk.Tk()
root.title("Table Mapping Application")
root.geometry("1000x600")

# Create a notebook (tab system)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create the "Mapping" tab frame
mapping_tab = ttk.Frame(notebook)
notebook.add(mapping_tab, text="Mapping")

# Frame for the table creation and mapping functionality in the "Mapping" tab
frame = tk.Frame(mapping_tab)
frame.pack(pady=20, padx=20)

# Create headers for the table
headers = ["Source Schema", "Source Table", "Source Column", "Source Type", 
           "Target Schema", "Target Table", "Target Column", "Target Type", "Actions"]
for col, header in enumerate(headers):
    tk.Label(frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=col, padx=5, pady=5)

# List to store the rows (widgets) for the mapping table
target_columns = []
target_column_widgets = []

# Function to add a new row (target column)
def add_target_column():
    row = len(target_columns) + 1
    
    # Source Schema, Table, Column, and Type
    source_schema_entry = tk.Entry(frame, width=15)
    source_schema_entry.grid(row=row, column=0, padx=5, pady=5)

    source_table_entry = tk.Entry(frame, width=15)
    source_table_entry.grid(row=row, column=1, padx=5, pady=5)

    source_column_entry = tk.Entry(frame, width=15)
    source_column_entry.grid(row=row, column=2, padx=5, pady=5)

    source_type_entry = tk.Entry(frame, width=15)
    source_type_entry.grid(row=row, column=3, padx=5, pady=5)
    
    # Target Schema, Table, Column, and Type
    target_schema_entry = tk.Entry(frame, width=15)
    target_schema_entry.grid(row=row, column=4, padx=5, pady=5)

    target_table_entry = tk.Entry(frame, width=15)
    target_table_entry.grid(row=row, column=5, padx=5, pady=5)

    target_column_entry = tk.Entry(frame, width=15)
    target_column_entry.grid(row=row, column=6, padx=5, pady=5)

    target_type_entry = tk.Entry(frame, width=15)
    target_type_entry.grid(row=row, column=7, padx=5, pady=5)
    
    # Buttons for actions
    # Add button (blue)
    add_button = tk.Button(frame, text="+", bg="blue", fg="white", command=add_target_column)
    add_button.grid(row=row, column=8, padx=5, pady=5)
    
    # Delete button (red)
    delete_button = tk.Button(frame, text="X", bg="red", fg="white", command=lambda idx=len(target_columns): delete_target_column(idx))
    delete_button.grid(row=row, column=9, padx=5, pady=5)
    
    # Save button (green)
    save_button = tk.Button(frame, text="✓", bg="green", fg="white", command=lambda idx=len(target_columns): save_row(idx))
    save_button.grid(row=row, column=10, padx=5, pady=5)

    # Append the new column info to the list
    target_columns.append({
        "source_schema": source_schema_entry,
        "source_table": source_table_entry,
        "source_column": source_column_entry,
        "source_type": source_type_entry,
        "target_schema": target_schema_entry,
        "target_table": target_table_entry,
        "target_column": target_column_entry,
        "target_type": target_type_entry,
    })
    target_column_widgets.append({
        "save_button": save_button,
        "edit_button": None  # Placeholder for the future edit button
    })

# Function to delete a row
def delete_target_column(index):
    for widget in frame.grid_slaves():
        if int(widget.grid_info()["row"]) == index + 1:
            widget.grid_forget()
    target_columns.pop(index)
    target_column_widgets.pop(index)

# Function to save a row (convert input fields to labels)
def save_row(index):
    for key, entry in target_columns[index].items():
        # Convert each entry to label
        value = entry.get()
        label = tk.Label(frame, text=value)
        label.grid(row=index + 1, column=list(target_columns[index].keys()).index(key), padx=5, pady=5)
        entry.grid_forget()
        target_columns[index][key] = label

    # Hide the save button after saving
    target_column_widgets[index]["save_button"].grid_forget()

    # Enable editing later by providing an "edit" button
    edit_button = tk.Button(frame, text="✏️", command=lambda idx=index: edit_row(idx))
    edit_button.grid(row=index + 1, column=10, padx=5, pady=5)
    target_column_widgets[index]["edit_button"] = edit_button

# Function to edit a row (convert labels back to entry fields)
def edit_row(index):
    for key, label in target_columns[index].items():
        # Convert label back to entry
        value = label.cget("text")
        entry = tk.Entry(frame, width=15)
        entry.insert(0, value)
        entry.grid(row=index + 1, column=list(target_columns[index].keys()).index(key), padx=5, pady=5)
        label.grid_forget()
        target_columns[index][key] = entry
    
    # Replace edit button with save button again
    target_column_widgets[index]["edit_button"].grid_forget()
    target_column_widgets[index]["save_button"].grid(row=index + 1, column=10, padx=5, pady=5)

# --------- Save Button at the bottom of the window ---------
save_frame = tk.Frame(root)
save_frame.pack(side="bottom", fill="x")

# "Save" button for the entire form
save_button = tk.Button(save_frame, text="Save All Mappings", command=lambda: print("Save all mappings"))
save_button.pack(side="left", padx=20, pady=10)

# Add an initial row on application load
add_target_column()

# Run the Tkinter main loop
root.mainloop()
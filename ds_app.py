import tkinter as tk
from tkinter import ttk

# Create the main window
root = tk.Tk()
root.title("Table Mapping Application")
root.geometry("1000x600")  # Set a default size

# Create a notebook (tab system)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create the "Mapping" tab frame
mapping_tab = ttk.Frame(notebook)
notebook.add(mapping_tab, text="Mapping")

# Frame for the table creation and mapping functionality in the "Mapping" tab
frame = tk.Frame(mapping_tab)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# Allow dynamic resizing in the grid for rows and columns
for i in range(9):  # 9 because we have 9 columns
    frame.columnconfigure(i, weight=1)  # Enable columns to expand equally

# Create headers for the table
headers = ["Source Schema", "Source Table", "Source Column", "Source Type", 
           "Target Schema", "Target Table", "Target Column", "Target Type", "Actions"]
for col, header in enumerate(headers):
    tk.Label(frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

# List to store the rows (widgets) for the mapping table
target_columns = []
target_column_widgets = []

# Function to limit the length of text in an entry widget
def limit_size(event):
    if len(event.widget.get()) > 100:
        event.widget.delete(100, tk.END)

# Function to add a new row (target column)
def add_target_column():
    row = len(target_columns) + 1
    
    # Source Schema, Table, Column, and Type with borders
    source_schema_entry = create_entry_with_border(frame, row, 0)
    source_table_entry = create_entry_with_border(frame, row, 1)
    source_column_entry = create_entry_with_border(frame, row, 2)
    source_type_entry = create_entry_with_border(frame, row, 3)
    
    # Target Schema, Table, Column, and Type with borders
    target_schema_entry = create_entry_with_border(frame, row, 4)
    target_table_entry = create_entry_with_border(frame, row, 5)
    target_column_entry = create_entry_with_border(frame, row, 6)
    target_type_entry = create_entry_with_border(frame, row, 7)
    
    # Buttons for actions
    # Add button (blue)
    add_button = tk.Button(frame, text="+", bg="blue", fg="white", command=add_target_column)
    add_button.grid(row=row, column=8, padx=5, pady=5, sticky="nsew")
    
    # Delete button (red)
    delete_button = tk.Button(frame, text="X", bg="red", fg="white", command=lambda idx=len(target_columns): delete_target_column(idx))
    delete_button.grid(row=row, column=9, padx=5, pady=5, sticky="nsew")
    
    # Save button (green)
    save_button = tk.Button(frame, text="✓", bg="green", fg="white", command=lambda idx=len(target_columns): save_row(idx))
    save_button.grid(row=row, column=10, padx=5, pady=5, sticky="nsew")

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
        label = create_label_with_border(frame, value, index + 1, list(target_columns[index].keys()).index(key))
        entry.grid_forget()
        target_columns[index][key] = label

    # Hide the save button after saving
    target_column_widgets[index]["save_button"].grid_forget()

    # Enable editing later by providing an "edit" button
    edit_button = tk.Button(frame, text="✏️", command=lambda idx=index: edit_row(idx))
    edit_button.grid(row=index + 1, column=10, padx=5, pady=5, sticky="nsew")
    target_column_widgets[index]["edit_button"] = edit_button

# Function to edit a row (convert labels back to entry fields with old values retained)
def edit_row(index):
    for key, label in target_columns[index].items():
        # Convert label back to entry, keeping the old value
        value = label.cget("text")
        entry = create_entry_with_border(frame, index + 1, list(target_columns[index].keys()).index(key), value)
        label.grid_forget()
        target_columns[index][key] = entry
    
    # Replace edit button with save button again
    target_column_widgets[index]["edit_button"].grid_forget()
    target_column_widgets[index]["save_button"].grid(row=index + 1, column=10, padx=5, pady=5, sticky="nsew")

# Helper function to create an entry widget with a border
def create_entry_with_border(parent, row, col, initial_value=""):
    border_frame = tk.Frame(parent, highlightbackground="black", highlightthickness=1)
    border_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    entry = tk.Entry(border_frame, width=15)
    entry.insert(0, initial_value)
    entry.pack(fill="both", expand=True)
    
    # Set up a binding to limit the size of the text
    entry.bind('<KeyRelease>', limit_size)
    return entry

# Helper function to create a label with a border
def create_label_with_border(parent, text, row, col):
    border_frame = tk.Frame(parent, highlightbackground="black", highlightthickness=1)
    border_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    label = tk.Label(border_frame, text=text, width=15)
    label.pack(fill="both", expand=True)
    return label

# --------- Save Button at the bottom of the window ---------
save_frame = tk.Frame(root)
save_frame.pack(side="bottom", fill="x")

# "Save" button for the entire form
save_button = tk.Button(save_frame, text="Save All Mappings", command=lambda: print("Save all mappings"))
save_button.pack(side="left", padx=20, pady=10)

# Add an initial row on application load
add_target_column()

# Allow dynamic resizing in the root window and main frame
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mapping_tab.columnconfigure(0, weight=1)
mapping_tab.rowconfigure(0, weight=1)

# Run the Tkinter main loop
root.mainloop()
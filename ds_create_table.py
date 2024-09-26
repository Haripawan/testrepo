import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Create the main window
root = tk.Tk()
root.title("Table Mapping Application")
root.geometry("1200x600")  # Set a default size

# Create a frame to hold the tabs and logged-in info in the same line
top_frame = tk.Frame(root)
top_frame.pack(fill="x", pady=5)

# Define logged-in user
logged_in_user = "User123"  # You can dynamically change this value

# Create a notebook (tab system) with a custom 3D style
style = ttk.Style()
style.theme_use('clam')

# Modify the tab style to make it 3D and distinguishable
style.configure("CustomNotebook.TNotebook.Tab",
                padding=[10, 5],  # Padding inside the tab
                relief="raised",   # Raised effect (3D-like)
                background="lightgray",  # Background color of unselected tabs
                foreground="black",  # Text color
                font=('Arial', 10, 'bold'))  # Font for the tabs

# Modify the selected tab appearance
style.map("CustomNotebook.TNotebook.Tab",
          background=[("selected", "lightblue")],  # Background color when the tab is selected
          foreground=[("selected", "darkblue")],  # Text color when selected
          expand=[("selected", [1, 1, 1, 0])],    # Slight expansion for 3D effect
          relief=[("selected", "solid")])         # Change the relief to a more solid look when selected

# Create the notebook and place it on the left side of the top_frame
notebook = ttk.Notebook(top_frame, style="CustomNotebook.TNotebook")

# Use grid to place notebook and logged-in label in the same row
notebook.grid(row=0, column=0, sticky="nsew", padx=(10, 0))

# Create the "Logged in as <user>" label and place it in the same row
logged_in_label = tk.Label(top_frame, text=f"Logged in as {logged_in_user}", font=("Arial", 12, "italic"))
logged_in_label.grid(row=0, column=1, sticky="e", padx=(10, 10))

# Make sure the notebook expands properly while keeping the label to the right
top_frame.grid_columnconfigure(0, weight=1)

# Create tabs
mapping_tab = ttk.Frame(notebook)
extra_field_tab = ttk.Frame(notebook)
create_table_tab = ttk.Frame(notebook)  # New tab for "Create Table"

# Add tabs to the notebook
notebook.add(mapping_tab, text="Mapping")
notebook.add(extra_field_tab, text="Extra Field")
notebook.add(create_table_tab, text="Create Table")  # Add "Create Table" tab

# ------------------ Create Table Tab ------------------------

def show_create_form():
    # Show form to create table
    table_form.pack(fill="x", pady=10)
    column_frame.pack(fill="x", pady=10)

def add_column():
    # Add new row for column entry
    row = len(columns) + 1
    
    col_name_entry = ttk.Entry(column_frame, width=20)
    col_name_entry.grid(row=row, column=0, padx=5, pady=5)
    
    col_data_type_entry = ttk.Entry(column_frame, width=15)
    col_data_type_entry.grid(row=row, column=1, padx=5, pady=5)
    
    nullable_option = ttk.Combobox(column_frame, values=["Yes", "No"], width=10)
    nullable_option.grid(row=row, column=2, padx=5, pady=5)
    
    key_field_option = ttk.Combobox(column_frame, values=["Yes", "No"], width=10)
    key_field_option.grid(row=row, column=3, padx=5, pady=5)
    
    columns.append((col_name_entry, col_data_type_entry, nullable_option, key_field_option))

# Define layout for "Create Table"
create_table_frame = tk.Frame(create_table_tab)
create_table_frame.pack(fill="both", expand=True)

# Buttons for Create and Modify Table
create_button = tk.Button(create_table_frame, text="Create Table", command=show_create_form, width=15)
create_button.pack(side="left", padx=10, pady=20)

modify_button = tk.Button(create_table_frame, text="Modify Table", state="disabled", width=15)  # Disable Modify for now
modify_button.pack(side="left", padx=10, pady=20)

# Table creation form (initially hidden)
table_form = tk.Frame(create_table_tab)
tk.Label(table_form, text="Table Name:", font=("Arial", 10)).pack(side="left", padx=5)
table_name_entry = ttk.Entry(table_form, width=30)
table_name_entry.pack(side="left", padx=5)

# Frame for column details (initially hidden)
column_frame = tk.Frame(create_table_tab)

# Column headers
tk.Label(column_frame, text="Column Name", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
tk.Label(column_frame, text="Data Type", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5)
tk.Label(column_frame, text="Nullable", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
tk.Label(column_frame, text="Key Field", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5)

# "+" button to add more columns
add_column_button = tk.Button(column_frame, text="+", command=add_column, font=("Arial", 12, "bold"), width=3, bg="blue", fg="white")
add_column_button.grid(row=0, column=4, padx=10)

# List to store column details
columns = []

# Add one column row by default
add_column()

# ------------------- End of Create Table Tab ------------------

# Start the main application loop
root.mainloop()
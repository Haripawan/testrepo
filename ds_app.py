import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import io
import cairosvg

# Create the main window
root = tk.Tk()
root.title("Table Mapping Application")
root.geometry("1200x600")  # Set a default size

# Create a notebook (tab system)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Function to load SVG as PhotoImage using Pillow
def load_svg(svg_file, size=(20, 20)):
    # Convert SVG to PNG and load it
    png_data = cairosvg.svg2png(url=svg_file, output_width=size[0], output_height=size[1])
    img = Image.open(io.BytesIO(png_data))
    return ImageTk.PhotoImage(img)

# Load action button SVGs
plus_icon = load_svg("plus.svg")  # Replace with your file path
delete_icon = load_svg("delete.svg")  # Replace with your file path
tick_icon = load_svg("tick.svg")  # Replace with your file path
pencil_icon = load_svg("pencil.svg")  # Replace with your file path

# Define Scrollable Frame for Mapping tab
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# Create the "Mapping" tab frame
mapping_tab = ttk.Frame(notebook)
notebook.add(mapping_tab, text="Mapping")

# Add scrollable frame to the mapping tab
scrollable_frame = ScrollableFrame(mapping_tab)
scrollable_frame.pack(fill="both", expand=True)

# Frame for the table creation and mapping functionality in the "Mapping" tab
frame = tk.Frame(scrollable_frame.scrollable_frame)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# Allow dynamic resizing in the grid for rows and columns
for i in range(13):  # 13 columns (due to added fields)
    frame.columnconfigure(i, weight=1)  # Enable columns to expand equally

# Create headers for the table
headers = ["Source Schema", "Source Table", "Source Column", "Source Type", "Mapping Type", 
           "Additional Field", "Target Schema", "Target Table", "Target Column", "Target Type", 
           "Actions"]
for col, header in enumerate(headers):
    tk.Label(frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

# List to store the rows (widgets) for the mapping table
target_columns = []
target_column_widgets = []

# Function to limit the length of text in an entry widget
def limit_size(event):
    if len(event.widget.get()) > 100:
        event.widget.delete(100, tk.END)

# Function to create an entry widget with a visible border
def create_entry_with_border(parent, row, column):
    entry = tk.Entry(parent, bd=2, relief="solid")  # Added border with 2px thickness and solid relief
    entry.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
    entry.bind("<KeyRelease>", limit_size)  # Bind to limit the length of input
    return entry

# Function to make row read-only
def make_row_read_only(row_idx):
    for entry in target_columns[row_idx].values():
        if isinstance(entry, tk.Entry):
            entry.config(state=tk.DISABLED)

# Function to enable row editing
def enable_row_editing(row_idx):
    for entry in target_columns[row_idx].values():
        if isinstance(entry, tk.Entry):
            entry.config(state=tk.NORMAL)

# Function to handle row save (tick button clicked)
def save_row(row_idx):
    make_row_read_only(row_idx)
    # Show pencil button after save
    target_column_widgets[row_idx]["save_button"].grid_forget()
    target_column_widgets[row_idx]["pencil_button"].grid(row=row_idx+1, column=10, padx=5, pady=5, sticky="nsew")

# Function to enable or disable delete button based on row count
def update_delete_buttons():
    if len(target_columns) <= 1:
        for widget in target_column_widgets:
            widget['delete_button'].config(state=tk.DISABLED)
    else:
        for widget in target_column_widgets:
            widget['delete_button'].config(state=tk.NORMAL)

# Function to handle mapping type change
def handle_mapping_type_change(row_idx):
    mapping_type = target_columns[row_idx]["mapping_type"].get()
    if mapping_type == "Derived":
        # Create extra text field if derived is selected
        extra_field_entry = create_entry_with_border(frame, row_idx + 1, 5)
        target_columns[row_idx]["extra_field"] = extra_field_entry

# Function to add a new row (target column)
def add_target_column():
    row = len(target_columns) + 1
    
    # Source Schema, Table, Column, and Type with borders
    source_schema_entry = create_entry_with_border(frame, row, 0)
    source_table_entry = create_entry_with_border(frame, row, 1)
    source_column_entry = create_entry_with_border(frame, row, 2)
    source_type_entry = create_entry_with_border(frame, row, 3)
    
    # Mapping Type Dropdown
    mapping_type_var = tk.StringVar()
    mapping_type_dropdown = ttk.Combobox(frame, textvariable=mapping_type_var)
    mapping_type_dropdown['values'] = ("Straight Move", "Derived")
    mapping_type_dropdown.current(0)  # Default to "Straight Move"
    mapping_type_dropdown.grid(row=row, column=4, padx=5, pady=5, sticky="nsew")
    mapping_type_dropdown.bind("<<ComboboxSelected>>", lambda event, idx=row: handle_mapping_type_change(idx))

    # Extra field for "Derived"
    extra_field_entry = None

    # Target Schema, Table, Column, and Type with borders
    target_schema_entry = create_entry_with_border(frame, row, 6)
    target_table_entry = create_entry_with_border(frame, row, 7)
    target_column_entry = create_entry_with_border(frame, row, 8)
    target_type_entry = create_entry_with_border(frame, row, 9)

    # Buttons for actions with SVG icons and consistent size
    button_width = 25  # Fixed button width
    
    # Add button (blue)
    add_button = tk.Button(frame, image=plus_icon, width=button_width, height=20, command=add_target_column)
    add_button.grid(row=row, column=11, padx=5, pady=5, sticky="nsew")
    
    # Delete button (red)
    delete_button = tk.Button(frame, image=delete_icon, width=button_width, height=20, command=lambda idx=len(target_columns): delete_target_column(idx))
    delete_button.grid(row=row, column=12, padx=5, pady=5, sticky="nsew")
    
    # Save button (green)
    save_button = tk.Button(frame, image=tick_icon, width=button_width, height=20, command=lambda idx=len(target_columns): save_row(idx))
    save_button.grid(row=row, column=10, padx=5, pady=5, sticky="nsew")
    
    # Pencil button for edit (hidden initially)
    pencil_button = tk.Button(frame, image=pencil_icon, width=button_width, height=20, command=lambda idx=row-1: enable_row_editing(idx))
    
    # Append the new column info to the list
    target_columns.append({
        "source_schema": source_schema_entry,
        "source_table": source_table_entry,
        "source_column": source_column_entry,
        "source_type": source_type_entry,
        "mapping_type": mapping_type_dropdown,
        "extra_field": extra_field_entry,
        "target_schema": target_schema_entry,
        "target_table": target_table_entry,
        "target_column": target_column_entry,
        "target_type": target_type_entry,
    })

    # Append the button widgets to the widget list
    target_column_widgets.append({
        "save_button": save_button,
        "delete_button": delete_button,
        "pencil_button": pencil_button
    })

    # Update delete button states
    update_delete_buttons()

# Function to delete a row
def delete_target_column(idx):
    if len(target_columns) > 1:
        # Remove widgets from grid and delete the row data
        for col in target_columns[idx].values():
            if isinstance(col, list):  # For "extra_field"
                for widget in col:
                    widget.grid_forget()
            else:
                col.grid_forget()
        
        # Remove the row from the lists
        target_columns.pop(idx)
        target_column_widgets.pop(idx)
    
    # Rearrange remaining rows
    for i, target_row in enumerate(target_columns):
        for j, widget in enumerate(target_row.values()):
            widget.grid(row=i+1, column=j, padx=5, pady=5, sticky="nsew")
    
    # Update delete button states
    update_delete_buttons()

# Initially add one row
add_target_column()

# Start the main application loop
root.mainloop()
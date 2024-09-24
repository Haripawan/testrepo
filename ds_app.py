import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
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
for i in range(12):  # 12 because we have 12 columns including actions
    frame.columnconfigure(i, weight=1)  # Enable columns to expand equally

# Create headers for the table
headers = ["Source Schema", "Source Table", "Source Column", "Source Type", 
           "Target Schema", "Target Table", "Target Column", "Target Type", 
           "Mapping Type", "Actions"]
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
    
    # Dropdown for Mapping Type (Straight Move or Derived)
    mapping_type_var = tk.StringVar()
    mapping_type_dropdown = ttk.Combobox(frame, textvariable=mapping_type_var)
    mapping_type_dropdown['values'] = ("Straight Move", "Derived")
    mapping_type_dropdown.current(0)  # Default to "Straight Move"
    mapping_type_dropdown.grid(row=row, column=8, padx=5, pady=5, sticky="nsew")
    mapping_type_dropdown.bind("<<ComboboxSelected>>", lambda event, idx=row: handle_mapping_type_change(idx))

    # Buttons for actions with SVG icons and consistent size
    button_width = 25  # Fixed button width
    
    # Add button (blue)
    add_button = tk.Button(frame, image=plus_icon, width=button_width, height=20, command=add_target_column)
    add_button.grid(row=row, column=9, padx=5, pady=5, sticky="nsew")
    
    # Delete button (red)
    delete_button = tk.Button(frame, image=delete_icon, width=button_width, height=20, command=lambda idx=len(target_columns): delete_target_column(idx))
    delete_button.grid(row=row, column=10, padx=5, pady=5, sticky="nsew")
    
    # Save button (green)
    save_button = tk.Button(frame, image=tick_icon, width=button_width, height=20, command=lambda idx=len(target_columns): save_row(idx))
    save_button.grid(row=row, column=11, padx=5, pady=5, sticky="nsew")

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
        "mapping_type": mapping_type_dropdown,
        "extra_source_fields": []  # This will store additional source fields for Derived type
    })
    target_column_widgets.append({
        "save_button": save_button,
        "edit_button": None  # Placeholder for the future edit button
    })

# Other necessary functions (save_row, delete_target_column, etc.) remain as in the previous code
# with all updated logic from the previous steps.
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json

# Create the main window
root = tk.Tk()
root.title("Table Mapping Application")
root.geometry("1200x600")  # Set a default size

# Define logged-in user
logged_in_user = "User123"  # You can dynamically change this value
# Add "Logged in as <user>" at the top
logged_in_label = tk.Label(root, text=f"Logged in as {logged_in_user}", font=("Arial", 12, "italic"), anchor="w")
logged_in_label.pack(fill="x", pady=5)

# Create a notebook (tab system) with a custom 3D style
style = ttk.Style()

# Set the theme to something that supports tab customization (like 'default' or 'clam')
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

# Apply the custom style to the Notebook
notebook = ttk.Notebook(root, style="CustomNotebook.TNotebook")
notebook.pack(fill="both", expand=True)

# Create tabs
mapping_tab = ttk.Frame(notebook)
extra_field_tab = ttk.Frame(notebook)

# Add tabs to the notebook
notebook.add(mapping_tab, text="Mapping")
notebook.add(extra_field_tab, text="Extra Field")

# Scrollable frame for Mapping tab (for additional rows or elements)
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

# Add the scrollable frame to the mapping tab
scrollable_frame = ScrollableFrame(mapping_tab)
scrollable_frame.pack(fill="both", expand=True)

# You can now add content to the scrollable_frame as needed
frame = tk.Frame(scrollable_frame.scrollable_frame)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# Example headers for mapping table
headers = ["Source Schema", "Source Table", "Source Column", "Source Type", "Mapping Type", 
           "Extra Field", "Target Schema", "Target Table", "Target Column", "Target Type", "Actions"]
for col, header in enumerate(headers):
    tk.Label(frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

# Add more code for table rows, buttons, and other features...

# Example Print Data button
print_button = tk.Button(root, text="Print Data", command=lambda: messagebox.showinfo("Mapped Data", json.dumps({"example": "data"})))
print_button.pack(pady=10)

# Start the main application loop
root.mainloop()
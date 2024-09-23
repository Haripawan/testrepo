import tkinter as tk
from tkinter import messagebox

# Create the main window
root = tk.Tk()
root.title("Simple Desktop App")
root.geometry("300x200")

# Define a function that will be triggered when the button is clicked
def on_button_click():
    messagebox.showinfo("Message", "Hello, World!")

# Add a label
label = tk.Label(root, text="Welcome to your app!", font=("Arial", 14))
label.pack(pady=20)

# Add a button
button = tk.Button(root, text="Click Me", command=on_button_click, font=("Arial", 12))
button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
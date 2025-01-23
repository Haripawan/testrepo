import tkinter as tk
from tkinter import messagebox
import random

# Sample images and descriptions
questions = [
    {
        "image": "path_to_image1.png",  # Replace with actual image paths
        "options": ["A Cat", "A Dog", "A Bird", "A Fish"],
        "answer": "A Cat"
    },
    {
        "image": "path_to_image2.png",
        "options": ["A Car", "A Bicycle", "A Train", "An Airplane"],
        "answer": "A Bicycle"
    },
]

class ImageDragDropGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Drag-and-Drop Game")
        self.root.geometry("800x600")
        self.score = 0
        self.current_question_index = 0
        self.dragged_item = None

        # Header
        self.header = tk.Label(self.root, text="Score: 0", font=("Arial", 16))
        self.header.pack(pady=10)

        # Image canvas
        self.canvas = tk.Canvas(self.root, width=400, height=300, bg="lightgray")
        self.canvas.pack(pady=20)
        self.image_id = None

        # Dragging area
        self.drag_area = tk.Frame(self.root, bg="lightblue", width=400, height=50)
        self.drag_area.pack(pady=10)

        # Option boxes
        self.option_frames = []
        for i in range(4):
            frame = tk.Frame(self.root, width=150, height=50, bg="white", relief="ridge", borderwidth=2)
            frame.pack_propagate(False)  # Prevent resizing with content
            frame.place(x=150 + i * 160, y=400)  # Position the boxes
            frame.bind("<Enter>", lambda event, i=i: self.on_drag_enter(event, i))
            frame.bind("<Leave>", lambda event, i=i: self.on_drag_leave(event, i))
            frame.bind("<ButtonRelease-1>", lambda event, i=i: self.check_answer(event, i))
            label = tk.Label(frame, text="", font=("Arial", 12), bg="white")
            label.pack(expand=True, fill="both")
            self.option_frames.append(frame)

        # Reset button
        self.reset_button = tk.Button(self.root, text="Reset", font=("Arial", 14), command=self.reset_game)
        self.reset_button.pack(pady=20)

        # Load the first question
        self.load_question()

    def load_question(self):
        """Loads the current question and updates the UI."""
        question = questions[self.current_question_index]

        # Display the image
        self.img = tk.PhotoImage(file=question["image"])  # Replace with the correct image format
        if self.image_id:
            self.canvas.delete(self.image_id)
        self.image_id = self.canvas.create_image(200, 150, image=self.img)

        # Update the option frames
        for i, frame in enumerate(self.option_frames):
            label = frame.winfo_children()[0]
            label.config(text=question["options"][i], bg="white")

    def on_drag_enter(self, event, i):
        """Handles when the dragged image enters a frame."""
        self.option_frames[i].config(bg="lightyellow")

    def on_drag_leave(self, event, i):
        """Handles when the dragged image leaves a frame."""
        self.option_frames[i].config(bg="white")

    def check_answer(self, event, i):
        """Checks if the answer is correct when the image is dropped."""
        question = questions[self.current_question_index]
        selected_option = self.option_frames[i].winfo_children()[0].cget("text")

        if selected_option == question["answer"]:
            self.score += 1
            self.option_frames[i].config(bg="lightgreen")
        else:
            self.option_frames[i].config(bg="lightcoral")
            # Highlight the correct answer
            for frame in self.option_frames:
                if frame.winfo_children()[0].cget("text") == question["answer"]:
                    frame.config(bg="lightgreen")
                    break

        # Update the score
        self.header.config(text=f"Score: {self.score}")

        # Proceed to the next question
        self.root.after(2000, self.next_question)

    def next_question(self):
        """Loads the next question or shows a game-over message."""
        self.current_question_index += 1
        if self.current_question_index >= len(questions):
            messagebox.showinfo("Game Over", f"Game Over! Your final score is: {self.score}")
            self.reset_game()
        else:
            self.load_question()

    def reset_game(self):
        """Resets the game to the initial state."""
        self.score = 0
        self.current_question_index = 0
        self.header.config(text="Score: 0")
        for frame in self.option_frames:
            frame.config(bg="white")
        self.load_question()


# Run the game
root = tk.Tk()
game = ImageDragDropGame(root)
root.mainloop()
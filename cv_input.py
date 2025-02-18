import cv2
import tkinter as tk
from tkinter import Label, Canvas, Frame
from PIL import Image, ImageTk
from cv_analyze_cube import analyze_rubiks_cube

class CubeCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rubik's Cube Capture")
        self.root.geometry("750x600")  # Increase GUI size to fit both views
        
        # Try different camera indices until we find one that works
        self.cap = None
        for i in range(5):  # Try indices 0, 1, 2, 3, 4
            cap = cv2.VideoCapture(i)
            ret, frame = cap.read()  # Try capturing a frame
            if ret and frame is not None:
                self.cap = cap
                print(f"Using camera index {i}")
                break
            else:
                cap.release()  # Release the failed capture
        
        if self.cap is None:
            raise RuntimeError("No working camera found!")
        
        self.frame = Frame(self.root, bg="lightgray")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.instruction_label = Label(self.frame, text="Align the Rubik's Cube in the correct color square and press Enter to Capture.", bg="lightgray", font=("Arial", 12))
        self.instruction_label.pack(pady=10)
        
        self.canvas_frame = Frame(self.frame)
        self.canvas_frame.pack()
        
        # Camera view
        self.camera_label = Label(self.canvas_frame, text="Live Camera View (Place cube in BLUE box)", font=("Arial", 10), bg="blue", fg="white")
        self.camera_label.grid(row=0, column=0, pady=5)
        
        self.canvas = Canvas(self.canvas_frame, width=300, height=300, bg="black", highlightbackground="blue", highlightthickness=5)
        self.canvas.grid(row=1, column=0, padx=10)
        
        # Captured image view
        self.captured_label = Label(self.canvas_frame, text="Captured Image (Captured in GREEN box)", font=("Arial", 10), bg="green", fg="white")
        self.captured_label.grid(row=0, column=1, pady=5)
        
        self.captured_canvas = Canvas(self.canvas_frame, width=300, height=300, bg="white", highlightbackground="green", highlightthickness=5)
        self.captured_canvas.grid(row=1, column=1, padx=10)
        
        # Add result display area
        self.result_label = Label(self.frame, text="Analysis Results:", font=("Arial", 12), bg="lightgray")
        self.result_label.pack(pady=5)
        
        self.result_text = Label(self.frame, text="No cube analyzed yet", font=("Arial", 10), bg="lightgray")
        self.result_text.pack()
        
        # Add frame for cube side inputs
        self.sides_frame = Frame(self.frame, bg="lightgray")
        self.sides_frame.pack(pady=10)
        
        # Create text entries for each cube side
        self.side_entries = []
        side_labels = [
            "Yellow side (orange top)",
            "Blue side (yellow top)",
            "Red side (yellow top)",
            "Green side (yellow top)",
            "Orange side (yellow top)",
            "White side (red top)"
        ]
        
        self.selected_entry_index = 0  # Track which entry is currently selected
        
        for i, label in enumerate(side_labels):
            side_frame = Frame(self.sides_frame, bg="lightgray")
            side_frame.pack(pady=2)
            
            Label(side_frame, text=label, bg="lightgray", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(side_frame, width=20)
            entry.pack(side=tk.LEFT)
            entry.bind('<FocusIn>', lambda e, idx=i: self.on_entry_select(idx))
            self.side_entries.append(entry)
        
        # Highlight the first entry by default
        self.side_entries[0].config(bg='lightblue')
        
        self.root.bind("<Return>", self.capture_image)  # Bind Enter key to capture function
        
        self.update_frame()
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (300, 300))  # Resize frame to match canvas
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.delete("all")  # Clear previous frame before updating
            self.canvas.create_image(150, 150, image=imgtk)
            self.canvas.imgtk = imgtk
        
        self.root.after(33, self.update_frame)  # Update at ~30 FPS
    
    def on_entry_select(self, index):
        # Reset background of all entries
        for entry in self.side_entries:
            entry.config(bg='white')
        # Highlight selected entry
        self.side_entries[index].config(bg='lightblue')
        self.selected_entry_index = index

    def capture_image(self, event=None):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (300, 300))
            img = Image.fromarray(frame)
            img.save("captured_cube.jpg")
            print("Image captured and saved as 'captured_cube.jpg'")
            
            imgtk = ImageTk.PhotoImage(image=img)
            self.captured_canvas.delete("all")
            self.captured_canvas.create_image(150, 150, image=imgtk)
            self.captured_canvas.imgtk = imgtk
            
            # Analyze the cube and display results
            try:
                grid = analyze_rubiks_cube(img)
                # Convert grid to sequence of first letters
                color_sequence = ''.join(color[0].upper() for row in grid for color in row)
                self.result_text.config(text=f"Cube colors: {color_sequence}")
                
                # Update the selected entry with the color sequence
                self.side_entries[self.selected_entry_index].delete(0, tk.END)
                self.side_entries[self.selected_entry_index].insert(0, color_sequence)
                
                # Move selection to next entry if not at the last one
                if self.selected_entry_index < 5:
                    next_index = self.selected_entry_index + 1
                    self.on_entry_select(next_index)
                
            except Exception as e:
                self.result_text.config(text=f"Error analyzing cube: {e}")
    
    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        
        
"""
yellow side with orange top
blue side with yellow top
red side with yellow top
green side with yellow top
orange side with yellow top
white side with red top
"""

if __name__ == "__main__":
    root = tk.Tk()
    app = CubeCaptureApp(root)
    root.mainloop()

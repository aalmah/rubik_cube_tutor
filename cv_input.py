import cv2
import tkinter as tk
from tkinter import ttk, Label, Canvas, Frame
from PIL import Image, ImageTk
from cv_analyze_cube import analyze_rubiks_cube
import subprocess
import sys

class CubeCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rubik's Cube Capture")
        self.root.geometry("800x600")  # Smaller window
        self.root.configure(bg="#f0f0f0")
        
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
        
        self.frame = Frame(self.root, bg="#f0f0f0")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Title with compact styling
        title_label = Label(self.frame, 
                          text="Rubik's Cube Scanner", 
                          bg="#f0f0f0", 
                          font=("Arial", 20, "bold"),
                          fg="#2c3e50")
        title_label.pack(pady=(0, 10))
        
        self.instruction_label = Label(self.frame, 
                                     text="Align cube and press Enter to capture", 
                                     bg="#f0f0f0", 
                                     font=("Arial", 11),
                                     fg="#34495e")
        self.instruction_label.pack(pady=(0, 10))
        
        # Camera views side by side
        self.canvas_frame = Frame(self.frame, bg="#f0f0f0")
        self.canvas_frame.pack(pady=5)
        
        # Camera view
        camera_container = Frame(self.canvas_frame, bg="#f0f0f0")
        camera_container.grid(row=0, column=0, padx=10)
        
        self.camera_label = Label(camera_container, 
                                text="Live Camera", 
                                font=("Arial", 10, "bold"),
                                bg="#3498db",
                                fg="white",
                                pady=3,
                                padx=10)
        self.camera_label.pack(pady=(0, 3))
        
        self.canvas = Canvas(camera_container, 
                           width=300, height=300,
                           bg="black",
                           highlightbackground="#3498db",
                           highlightthickness=2)
        self.canvas.pack()
        
        # Captured view
        captured_container = Frame(self.canvas_frame, bg="#f0f0f0")
        captured_container.grid(row=0, column=1, padx=10)
        
        self.captured_label = Label(captured_container,
                                  text="Captured",
                                  font=("Arial", 10, "bold"),
                                  bg="#27ae60",
                                  fg="white",
                                  pady=3,
                                  padx=10)
        self.captured_label.pack(pady=(0, 3))
        
        self.captured_canvas = Canvas(captured_container,
                                    width=300, height=300,
                                    bg="white",
                                    highlightbackground="#27ae60",
                                    highlightthickness=2)
        self.captured_canvas.pack()
        
        # Results section
        self.result_text = Label(self.frame,
                               text="No cube analyzed yet",
                               font=("Arial", 10),
                               bg="#f0f0f0",
                               fg="#7f8c8d")
        self.result_text.pack(pady=5)
        
        # Side entries in two columns
        self.sides_frame = Frame(self.frame, bg="#f0f0f0")
        self.sides_frame.pack(pady=5)
        
        self.side_entries = []
        side_labels = [
            "Yellow side (orange top)",
            "Blue side (yellow top)",
            "Red side (yellow top)",
            "Green side (yellow top)",
            "Orange side (yellow top)",
            "White side (red top)"
        ]
        
        self.selected_entry_index = 0
        
        # Create entries in 2 columns
        for i, label in enumerate(side_labels):
            row = i % 3
            col = i // 3
            
            side_frame = Frame(self.sides_frame, bg="#f0f0f0")
            side_frame.grid(row=row, column=col, pady=2, padx=5)
            
            Label(side_frame,
                 text=label,
                 bg="#f0f0f0",
                 font=("Arial", 10),
                 width=18,
                 anchor='e').pack(side=tk.LEFT, padx=5)
            
            entry = tk.Entry(side_frame,
                           width=15,
                           font=("Arial", 10),
                           relief="solid",
                           bd=1)
            entry.pack(side=tk.LEFT)
            entry.bind('<FocusIn>', lambda e, idx=i: self.on_entry_select(idx))
            self.side_entries.append(entry)
        
        # Highlight first entry
        self.side_entries[0].config(bg='#e8f0fe')
        
        shortcut_label = Label(self.frame,
                             text="Press Enter to capture",
                             font=("Arial", 9, "italic"),
                             bg="#f0f0f0",
                             fg="#95a5a6")
        shortcut_label.pack(pady=5)
        
        self.root.bind("<Return>", self.capture_image)
        
        # Reduce update frequency
        self.update_interval = 50  # 20 FPS instead of 30
        self.update_frame()
        
        # Add solve button at the bottom (initially disabled)
        self.solve_button = ttk.Button(
            self.frame,
            text="Start Solving",
            command=self.launch_solver,
            state='disabled'
        )
        self.solve_button.pack(pady=10)
        
        # Bind entry changes to check completion
        for entry in self.side_entries:
            entry.bind('<KeyRelease>', self.check_entries_complete)
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Resize first to reduce processing load
            frame = cv2.resize(frame, (300, 300))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert directly to PhotoImage without using PIL unless necessary
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.delete("all")
            self.canvas.create_image(150, 150, image=img_tk)
            self.canvas.img_tk = img_tk  # Keep reference to prevent garbage collection
        
        self.root.after(self.update_interval, self.update_frame)
    
    def on_entry_select(self, index):
        # Reset background of all entries
        for entry in self.side_entries:
            entry.config(bg='white')
        # Highlight selected entry with a softer blue
        self.side_entries[index].config(bg='#e8f0fe')
        self.selected_entry_index = index

    def capture_image(self, event=None):
        ret, frame = self.cap.read()
        if ret:
            # Process captured image
            frame = cv2.resize(frame, (300, 300))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Only save if needed for analysis
            img = Image.fromarray(frame)
            
            # Update display
            img_tk = ImageTk.PhotoImage(image=img)
            self.captured_canvas.delete("all")
            self.captured_canvas.create_image(150, 150, image=img_tk)
            self.captured_canvas.img_tk = img_tk
            
            # Analyze the cube and display results
            try:
                grid = analyze_rubiks_cube(img)
                color_sequence = ''.join(color[0].lower() for row in grid for color in row)
                self.result_text.config(text=f"Cube colors: {color_sequence}")
                
                # Update the selected entry
                self.side_entries[self.selected_entry_index].delete(0, tk.END)
                self.side_entries[self.selected_entry_index].insert(0, color_sequence)
                
                # Move to next entry if possible
                if self.selected_entry_index < 5:
                    next_index = self.selected_entry_index + 1
                    self.on_entry_select(next_index)
                
            except Exception as e:
                self.result_text.config(text=f"Error analyzing cube: {e}")
    
    def check_entries_complete(self, event=None):
        # Enable solve button if all entries are filled
        if all(entry.get() for entry in self.side_entries):
            self.solve_button.config(state='normal')
        else:
            self.solve_button.config(state='disabled')
    
    def launch_solver(self):
        # Get all sides in the correct order
        cube_string = ''.join(entry.get() for entry in self.side_entries)
        
        # Launch the solver with the cube string as an argument
        subprocess.Popen([sys.executable, 'rubiks_tutor.py', cube_string])
        
        # Optionally close the capture window
        self.root.destroy()

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

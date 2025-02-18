import sys
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from rubik_solver.Solver import Solver
from rubik_solver.Solver.Beginner import WhiteCrossSolver, WhiteFaceSolver, SecondLayerSolver, YellowCrossSolver, YellowFaceSolver
from rubik_solver.NaiveCube import NaiveCube
from rubik_solver.Cubie import Cube
from rubik_solver.Move import Move
from visualize import visualize_rubiks_cube
import copy
from cv_input import CubeCaptureApp

class BeginnerSolverAnnotated(Solver):
    def solution(self):
        cube = copy.deepcopy(self.cube)
        solution = []
        step_name = []
        
        solution_step = WhiteCrossSolver.WhiteCrossSolver(cube).solution()
        step_name += ['White Cross'] * len(solution_step)
        solution += solution_step
        
        solution_step = WhiteFaceSolver.WhiteFaceSolver(cube).solution()
        step_name += ['White Side'] * len(solution_step)
        solution += solution_step
        
        solution_step = SecondLayerSolver.SecondLayerSolver(cube).solution()
        step_name += ['Second Layer'] * len(solution_step)
        solution += solution_step
        
        solution_step = YellowCrossSolver.YellowCrossSolver(cube).solution()
        step_name += ['Yellow Cross'] * len(solution_step)
        solution += solution_step
        
        solution_step = YellowFaceSolver.YellowFaceSolver(cube).solution()
        step_name += ['Yellow Cross'] * len(solution_step)
        solution += solution_step
        
        return [Move(m) for m in solution], step_name

def _check_valid_cube(cube):
    if isinstance(cube, str):
        c = NaiveCube()
        c.set_cube(cube)
        cube = c
    if isinstance(cube, NaiveCube):
        c = Cube()
        c.from_naive_cube(cube)
        cube = c
    if not isinstance(cube, Cube):
        raise ValueError('Cube is not one of (str, NaiveCube or Cubie.Cube)')
    return cube

def solve(cube):
    cube = _check_valid_cube(cube)
    solver = BeginnerSolverAnnotated(cube)
    return solver.solution()

class RubiksSolverGUI:
    def __init__(self, root, cube_string=None):
        self.root = root
        self.root.title("Rubik's Cube Solver")
        self.root.geometry("800x800")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize with provided cube string if available
        if cube_string:
            self.cube_string = cube_string
            self.solve_button = ttk.Button(main_frame, text="Solve", command=self.solve_cube)
            self.solve_button.pack(pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Click 'Solve' to begin")
        self.status_label.pack(pady=5)
        
        # Matplotlib canvas
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.axes = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(pady=5)
        
        self.prev_button = ttk.Button(nav_frame, text="Previous Move", command=self.apply_prev_move, state='disabled')
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(nav_frame, text="Next Move", command=self.apply_next_move, state='disabled')
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Move and step labels
        self.move_label = ttk.Label(main_frame, text="Enter a cube definition and click 'Solve'")
        self.move_label.pack(pady=5)
        
        self.step_label = ttk.Label(main_frame, text="")
        self.step_label.pack(pady=5)
        
        # Solution label
        self.solution_label = ttk.Label(main_frame, text="", wraplength=700)
        self.solution_label.pack(pady=5)
        
        # Initialize other attributes
        self.cube = None
        self.solution = None
        self.step_names = None
        self.move_index = 0
        self.cube_sides = [""] * 6
        
        # If cube string was provided, solve immediately
        if cube_string:
            self.solve_cube()
    
    def solve_cube(self):
        try:
            self.cube = _check_valid_cube(self.cube_string)
            self.solution, self.step_names = solve(self.cube_string)
            self.move_index = 0
            
            self.update_cube_display()
            self.update_solution_label()
            self.move_label.config(text="Click 'Next Move' to start")
            self.step_label.config(text="")
            
            self.next_button.config(state='normal')
            self.prev_button.config(state='disabled')
        except ValueError as e:
            self.move_label.config(text=f"Error: {str(e)}")
            self.step_label.config(text="")
            self.solution_label.config(text="")
            self.next_button.config(state='disabled')
            self.prev_button.config(state='disabled')
            self.axes.clear()
            self.canvas.draw()
    
    def update_solution_label(self):
        if self.move_index < len(self.solution):
            solution_text = ", ".join(str(move) for move in self.solution)
            self.solution_label.config(text=f"Full solution: {solution_text}")
    
    def apply_next_move(self):
        if self.move_index < len(self.solution):
            move = self.solution[self.move_index]
            step_name = self.step_names[self.move_index]
            self.cube.move(move)
            self.move_label.config(text=f"Move {self.move_index + 1}/{len(self.solution)}")
            self.step_label.config(text=f"Step: {step_name}")
            self.move_index += 1
            self.update_cube_display()
            self.update_solution_label()
            self.prev_button.config(state='normal')
            
            if self.move_index == len(self.solution):
                self.next_button.config(state='disabled')
                self.move_label.config(text="Solved!")
                self.step_label.config(text="Completed!")
    
    def apply_prev_move(self):
        if self.move_index > 0:
            self.move_index -= 1
            move = self.solution[self.move_index]
            step_name = self.step_names[self.move_index]
            inverse_move = self.get_inverse_move(move)
            self.cube.move(inverse_move)
            self.move_label.config(text=f"Move {self.move_index}/{len(self.solution)}: Undid {move}")
            self.step_label.config(text=f"Step: {step_name}")
            self.update_cube_display()
            self.update_solution_label()
            self.next_button.config(state='normal')
            
            if self.move_index == 0:
                self.prev_button.config(state='disabled')
                self.move_label.config(text="Initial state")
                self.step_label.config(text="")
    
    def get_inverse_move(self, move):
        if isinstance(move, str):
            move = Move(move)
        return move.reverse()
    
    def update_cube_display(self):
        self.axes.clear()
        visualize_rubiks_cube(self.cube.to_naive_cube().get_cube(), self.axes)
        self.canvas.draw()

def main():
    root = tk.Tk()
    # Check if cube string was provided as command line argument
    cube_string = sys.argv[1] if len(sys.argv) > 1 else None
    app = RubiksSolverGUI(root, cube_string)
    root.mainloop()

if __name__ == "__main__":
    main()
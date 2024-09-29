import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from rubik_solver.Solver import Solver
from rubik_solver.Solver.Beginner import WhiteCrossSolver, WhiteFaceSolver, SecondLayerSolver, YellowCrossSolver, YellowFaceSolver

from rubik_solver.NaiveCube import NaiveCube
from rubik_solver.Cubie import Cube
from rubik_solver.Move import Move

from visualize import visualize_rubiks_cube  # Assuming this function exists in your original code
import copy


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

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111, projection='3d')
        super(MatplotlibCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Rubik's Cube Solver")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add input box and solve button
        input_layout = QHBoxLayout()
        self.cube_input = QLineEdit()
        self.cube_input.setPlaceholderText("wowgybwyogygybyoggrowbrgywrborwggybrbwororbwborgowryby")
        self.cube_input.setText("wowgybwyogygybyoggrowbrgywrborwggybrbwororbwborgowryby")
        input_layout.addWidget(self.cube_input)
        
        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.solve_cube)
        input_layout.addWidget(self.solve_button)
        
        layout.addLayout(input_layout)

        self.canvas = MatplotlibCanvas(self, width=5, height=5, dpi=100)
        layout.addWidget(self.canvas)

        button_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("Previous Move")
        self.prev_button.clicked.connect(self.apply_prev_move)
        self.prev_button.setEnabled(False)  # Disabled initially
        button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next Move")
        self.next_button.clicked.connect(self.apply_next_move)
        button_layout.addWidget(self.next_button)

        layout.addLayout(button_layout)

        self.move_label = QLabel("Enter a cube definition and click 'Solve'")
        layout.addWidget(self.move_label)

        self.step_label = QLabel()
        layout.addWidget(self.step_label)

        # Add a label to display the full solution
        self.solution_label = QLabel()
        self.solution_label.setWordWrap(True)
        layout.addWidget(self.solution_label)

        # Initialize other attributes
        self.cube = None
        self.solution = None
        self.step_names = None
        self.move_index = 0

    def solve_cube(self):
        cube_string = self.cube_input.text().lower()
        try:
            self.cube = _check_valid_cube(cube_string)
            self.solution, self.step_names = solve(cube_string)
            self.move_index = 0
            
            self.update_cube_display()
            self.update_solution_label()
            self.move_label.setText("Click 'Next Move' to start")
            self.step_label.setText("")
            
            self.next_button.setEnabled(True)
            self.prev_button.setEnabled(False)
        except ValueError as e:
            self.move_label.setText(f"Error: {str(e)}")
            self.step_label.setText("")
            self.solution_label.setText("")
            self.next_button.setEnabled(False)
            self.prev_button.setEnabled(False)
            self.canvas.axes.clear()
            self.canvas.draw()

    def update_solution_label(self):
        solution_html = []
        for i, move in enumerate(self.solution):
            if i == self.move_index:
                solution_html.append(f'<span style="background-color: yellow;">{move}</span>')
            else:
                solution_html.append(str(move))
        self.solution_label.setText(f"Full solution: {', '.join(solution_html)}")

    def apply_next_move(self):
        if self.move_index < len(self.solution):
            move = self.solution[self.move_index]
            step_name = self.step_names[self.move_index]
            self.cube.move(move)
            self.move_label.setText(f"Move {self.move_index + 1}/{len(self.solution)}")
            self.step_label.setText(f"Step: {step_name}")
            self.move_index += 1
            self.update_cube_display()
            self.update_solution_label()
            self.prev_button.setEnabled(True)
        if self.move_index == len(self.solution):
            self.next_button.setEnabled(False)
            self.move_label.setText("Solved!")
            self.step_label.setText("Completed!")

    def apply_prev_move(self):
        if self.move_index > 0:
            self.move_index -= 1
            move = self.solution[self.move_index]
            step_name = self.step_names[self.move_index]
            inverse_move = self.get_inverse_move(move)
            self.cube.move(inverse_move)
            self.move_label.setText(f"Move {self.move_index}/{len(self.solution)}: Undid {move}")
            self.step_label.setText(f"Step: {step_name}")
            self.update_cube_display()
            self.update_solution_label()
            self.next_button.setEnabled(True)
        if self.move_index == 0:
            self.prev_button.setEnabled(False)
            self.move_label.setText("Initial state")
            self.step_label.setText("")

    def get_inverse_move(self, move):
        if isinstance(move, str):
            move = Move(move)
        return move.reverse()

    def update_cube_display(self):
        self.canvas.axes.clear()
        visualize_rubiks_cube(self.cube.to_naive_cube().get_cube(), self.canvas.axes)
        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
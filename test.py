import argparse
import time
import tkinter as tk
from rubik_solver.Solver import Solver, Beginner, CFOP, Kociemba
from rubik_solver.NaiveCube import NaiveCube
from rubik_solver.Cubie import Cube
from rubik_solver.Printer import TtyPrinter


METHODS = {
    'Beginner': Beginner.BeginnerSolver,
    'CFOP': CFOP.CFOPSolver,
    'Kociemba': Kociemba.KociembaSolver
}

def _check_valid_cube(cube):
    '''Checks if cube is one of str, NaiveCube or Cubie.Cube and returns
    an instance of Cubie.Cube'''
    
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

def solve(cube, method = Beginner.BeginnerSolver, *args, **kwargs):
    if isinstance(method, str):
        if not method in METHODS:
            raise ValueError('Invalid method name, must be one of (%s)' %
                ', '.join(METHODS.keys())
            )
        method = METHODS[method]

    if not issubclass(method, Solver):
        raise ValueError('Method %s is not a valid Solver subclass' %
            method.__class__.__name__
        )

    cube = _check_valid_cube(cube)

    solver = method(cube)

    return solver.solution(*args, **kwargs)

def pprint(cube, color = True):
    cube = _check_valid_cube(cube)
    printer = TtyPrinter(cube, color)
    printer.pprint()

def main(argv = None):
    arg_parser = argparse.ArgumentParser(description = 'rubik_solver command line tool')
    arg_parser.add_argument('-i', '--cube', dest = 'cube', required = True, help = 'Cube definition string')
    arg_parser.add_argument('-c', '--color', dest = 'color', default = True, action = 'store_false', help = 'Disable use of colors with TtyPrinter')
    arg_parser.add_argument('-s', '--solver', dest = 'solver', default = 'Beginner', choices = METHODS.keys(), help = 'Solver method to use')
    args = arg_parser.parse_args(argv)

    cube = args.cube.lower()
    print("Read cube", cube)
    pprint(cube, args.color)

    start = time.time()
    solution = solve(cube, METHODS[args.solver])
    print("Solution found in", time.time() - start, "seconds")
    
    cube_obj = _check_valid_cube(cube)
    move_index = 0

    def apply_next_move():
        nonlocal move_index
        if move_index < len(solution):
            move = solution[move_index]
            cube_obj.move(move)
            move_label.config(text=f"Move {move_index + 1}/{len(solution)}: {move}")
            update_cube_display()
            move_index += 1
        else:
            next_button.config(state=tk.DISABLED)
            move_label.config(text="Solved!")

    def update_cube_display():
        cube_display.delete("1.0", tk.END)
        printer = TtyPrinter(cube_obj, args.color)
        cube_display.insert(tk.END, printer.get_tty_output())

    # Create GUI
    root = tk.Tk()
    root.title("Rubik's Cube Solver")

    cube_display = tk.Text(root, height=20, width=40, font=("Courier", 12))
    cube_display.pack(pady=10)

    next_button = tk.Button(root, text="Next Move", command=apply_next_move)
    next_button.pack(pady=5)

    move_label = tk.Label(root, text="Click 'Next Move' to start")
    move_label.pack(pady=5)

    update_cube_display()

    print("Total moves:", len(solution))
    print("Solution:", ', '.join(map(str, solution)))

    root.mainloop()

if __name__ == "__main__":
    main()
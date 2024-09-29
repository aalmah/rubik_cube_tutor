import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import fire


def visualize_rubiks_cube(cube_config):
    if len(cube_config) != 54:
        raise ValueError("The cube configuration must be exactly 54 characters long.")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Define color mapping
    color_map = {
        'w': 'white',
        'y': 'yellow',
        'r': 'red',
        'o': 'orange',
        'g': 'green',
        'b': 'blue'
    }

    # Define the faces of the 3x3 Rubik's cube
    faces = []
    face_colors = []
    
    # Define the order of faces: top, left, front, right, back, bottom
    face_order = [0, 1, 2, 3, 4, 5]
    face_ranges = [(0, 9), (9, 18), (18, 27), (27, 36), (36, 45), (45, 54)]

    for face_idx, (start, end) in zip(face_order, face_ranges):
        face_config = cube_config[start:end]
        for i in range(3):
            for j in range(3):
                if face_idx == 0:  # Top face
                    faces.append([[j, 2-i, 3], [j+1, 2-i, 3], [j+1, 3-i, 3], [j, 3-i, 3]])
                elif face_idx == 1:  # Left face
                    faces.append([[0, j, 2-i], [0, j, 3-i], [0, j+1, 3-i], [0, j+1, 2-i]])
                elif face_idx == 2:  # Front face
                    faces.append([[j, 0, 2-i], [j+1, 0, 2-i], [j+1, 0, 3-i], [j, 0, 3-i]])
                elif face_idx == 3:  # Right face
                    faces.append([[3, j, 2-i], [3, j, 3-i], [3, j+1, 3-i], [3, j+1, 2-i]])
                elif face_idx == 4:  # Back face
                    faces.append([[2-j, 3, 2-i], [3-j, 3, 2-i], [3-j, 3, 3-i], [2-j, 3, 3-i]])
                elif face_idx == 5:  # Bottom face
                    faces.append([[j, i, 0], [j+1, i, 0], [j+1, i+1, 0], [j, i+1, 0]])
                
                color_char = face_config[i*3 + j]
                face_colors.append(color_map[color_char])

    # Plot each face
    for face, color in zip(faces, face_colors):
        poly3d = [[tuple(vertex) for vertex in face]]
        ax.add_collection3d(Poly3DCollection(poly3d, facecolors=color, linewidths=1, edgecolors='black', alpha=1))

    # Set the aspect ratio to be equal
    ax.set_box_aspect([3, 3, 3])

    # Hide the axes
    ax.axis('off')

    # Set the limits of the axes
    ax.set_xlim([0, 3])
    ax.set_ylim([0, 3])
    ax.set_zlim([0, 3])

    plt.show()

def main(cube_config='wowgybbwygyoybyogwwgrorwrbygorrggobrbwororbwbgygowryby'):
    visualize_rubiks_cube(cube_config)

if __name__ == '__main__':
    fire.Fire(main)
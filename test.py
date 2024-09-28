import rubik_solver
from rubik_solver import NaiveCube

cube_config = 'wowgybwyogygybyoggrowbrgywrborwggybrbwororbwborgowryby'
print(len(cube_config))

for i in range(6):
    print(cube_config[i*9: (i+1)*9])




# ME35 FROSTING MECHANISM TEAM FINAL PROJECT MAIN SCRIPT
# NECESSARY FOR USE:
# numpy
# GPIO
# sudo apt-get install python-rpi.gpio python3-rpi.gpio
# MotorKit
# sudo pip3 install adafruit-circuitpython-motorkit
# https://docs.circuitpython.org/projects/motorkit/en/latest/#
# Circuitpython Motor
# sudo pip3 install adafruit-circuitpython-motor
# https://docs.circuitpython.org/projects/motor/en/latest/index.html

from frosting_board import FrostingMainBoard
import numpy as np

def split_shapes(commands: list, cutoff_distance: int):
    shapes = []
    shapes.append([commands[0]])
    shape_iteration = 0

    for i in range(len(commands)-1):
        distance = math.sqrt((commands[i+1][1]-commands[i][1])**2 + (commands[i+1][0]-commands[i][0])**2)
        if distance > cutoff_distance:
            shape_iteration += 1
            shapes.append([])

        shapes[shape_iteration].append(commands[i+1])    
    
    return shapes


def main():
    main_board = FrostingMainBoard()
                    #    X  Y  E
    drawing = np.array(([0, 0, 0],
                    [50, 0, 1],
                    [50, 50, 0.7],
                    [0, 50, 0],
                    [0, 0, 0]))

    main_board.draw(drawing, int(input('Speed: ')), main_board.white_extruder)
    return

if __name__ == '__main__':
    main()

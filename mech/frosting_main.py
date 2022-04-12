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
import pandas as pd


def split_shapes(commands: list, cutoff_distance: int) -> np.ndarray:
    shapes = [[commands[0]]]
    shape_iteration = 0

    for i in range(len(commands) - 1):
        distance = np.sqrt((commands[i + 1][1] - commands[i][1]) ** 2 + (commands[i + 1][0] - commands[i][0]) ** 2)
        if distance > cutoff_distance:
            shape_iteration += 1
            shapes.append([])

        shapes[shape_iteration].append(commands[i + 1])

    return np.asarray(shapes)


def main():
    main_board = FrostingMainBoard()

    # Square test
    #                       X  Y  E
    # drawing = np.array(([0, 0, 0],
    #                     [50, 0, 0],
    #                     [50, 50, 0],
    #                     [0, 50, 0],
    #                     [0, 0, 0]))

    # Spiral test
    # theta = np.linspace(0.1, 1 * np.pi, 50)
    # r = 10 * theta
    # X = r * np.cos(theta)
    # Y = r * np.sin(theta)
    # E = np.zeros(np.size(X))
    # drawing = np.array(([X, Y, E])).T

    drawing = pd.read_csv('coords.csv').values

    main_board.draw(drawing, main_board.white_extruder)

    return


if __name__ == '__main__':
    main()

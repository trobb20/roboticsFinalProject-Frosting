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
from img_processing import run as run_img_processing
from img_processing import waitForUnload
import pandas as pd

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

    # wait for unload to finish
    waitForUnload()

    # Get the image files
    run_img_processing()

    # Convert them to our drawings
    white_drawing = pd.read_csv('bgd_coordinates.csv').values[:, 0:3]
    black_drawing = pd.read_csv('img_coordinates.csv').values[:, 0:3]

    print('Starting frosting machine!')
    print('Homing all...')
    main_board.home_all()
    print('Drawing white background...')
    main_board.draw(white_drawing, main_board.white_extruder)
    print('Homing all...')
    main_board.home_all()
    print('Drawing black image...')
    main_board.draw(black_drawing, main_board.black_extruder)
    print('Done!')

    return


if __name__ == '__main__':
    main()

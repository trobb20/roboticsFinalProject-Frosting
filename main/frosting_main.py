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
from e_stop import main as emergency_stop
import pandas as pd
import numpy as np

# Offset for black extruder
black_extruder_offset = 20


def main():
    try:
        main_board = FrostingMainBoard()

        print('Started frosting main script... would you like to wait for unload?')
        if input('y/n: ') == 'y':
            print("Waiting for unload...")
            # wait for unload to finish
            waitForUnload()
            print("Unloaded. Beginning frosting process.")
        else:
            print('Beginning frosting process.')

        print("Getting image...")
        # Get the image files
        run_img_processing()

        # Convert them to our drawings
        white_drawing = pd.read_csv('bgd_coordinates.csv').values[:, 0:3]
        black_drawing = pd.read_csv('img_coordinates.csv').values[:, 0:3]

        # Draw the white image
        print('Starting frosting!')
        print('Homing all...')
        main_board.home_all()
        print('Drawing white background...')
        main_board.draw(white_drawing, main_board.white_extruder)

        # Draw the black image
        print('Homing all...')
        main_board.home_all()
        print("Switching to black...")
        main_board.x_y_move(black_extruder_offset, 0)
        main_board.location = np.array((0, 0))
        print('Drawing black image...')
        main_board.draw(black_drawing, main_board.black_extruder)

        # Turn everything off
        main_board.x_axis.disable()
        main_board.y_axis.disable()
        main_board.white_extruder.coast()
        main_board.black_extruder.coast()
        print('Done!')
    except KeyboardInterrupt:
        emergency_stop()

    return


if __name__ == '__main__':
    main()

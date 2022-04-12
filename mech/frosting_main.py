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

def main():
    main_board = FrostingMainBoard()

    drawing = np.array(([0, 0],
                    [50, 0],
                    [50, 50],
                    [0, 50],
                    [0, 0]))

    main_board.draw(drawing)
    return

if __name__ == '__main__':
    main()

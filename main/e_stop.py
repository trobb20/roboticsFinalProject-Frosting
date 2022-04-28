# ME35: Robotics Final Project
# Teddy Robbins, Tufts University 2022.
#
# e_stop.py
#
# This script intends to emergency stop the robot by
# turning off all motors.

from frosting_board import FrostingMainBoard


def main():
    main_board = FrostingMainBoard()

    print("E-STOP!")

    main_board.x_axis.disable()
    main_board.y_axis.disable()
    main_board.white_extruder.stop()
    main_board.black_extruder.stop()

    print("Stopped all motors.")


if __name__ == '__main__':
    main()

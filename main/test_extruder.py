from frosting_board import FrostingMainBoard
import time


def main():
    b = FrostingMainBoard()

    extruder = input('Test white or black: w/b: ')
    if extruder == 'w':
        b.white_extruder.drive(1)
        time.sleep(1)
        b.white_extruder.drive(0)
    elif extruder == 'b':
        b.black_extruder.drive(1)
        time.sleep(1)
        b.black_extruder.drive(0)
        

if __name__ == '__main__':
    main()
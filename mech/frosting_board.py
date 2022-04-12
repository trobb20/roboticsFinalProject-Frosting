# ME35 FROSTING MECHANISM TEAM FINAL PROJECT
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

from frosting_motors import FrostingStepper, FrostingDCMotor
from adafruit_motorkit import MotorKit
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import numpy as np
import time


class FrostingMainBoard:
    def __init__(self):
        # Parameters
        x_steps_per_mm = 25
        y_steps_per_mm = 25
        self.default_speed = 20
        self.x_endstop = 23  # GPIO23
        self.y_endstop = 24  # GPIO24

        # Spatial planning
        self.x_position = 0
        self.y_position = 0
        self.location = np.array([self.x_position, self.y_position])

        # Motor driver boards
        try:
            self.stepper_kit = MotorKit()               # default board
        except Exception as e:
            print("Some problem initializing stepper board. Error:")
            print(e)
            return
        try:
            self.extruder_kit = MotorKit(address=0x61)  # Bridge jumper A0 on extruder board
        except Exception as e:
            print("Some problem initializing extruder board. Error:")
            print(e)
            return

        # Steppers
        self.x_axis = FrostingStepper(self.stepper_kit, 1, x_steps_per_mm)
        self.y_axis = FrostingStepper(self.stepper_kit, 2, y_steps_per_mm)

        # Extruders
        self.white_extruder = FrostingDCMotor(self.extruder_kit, 1)
        self.black_extruder = FrostingDCMotor(self.extruder_kit, 2)

        # Endstops
        GPIO.setmode(GPIO.BCM)  # Use GPIO pin numbering
        GPIO.setup(self.x_endstop, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.y_endstop, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def home_x_axis(self, timeout: int = 10, backoff_mm: int = -2) -> bool:
        """
        Homes x axis
        :param timeout: default number of seconds before timing out with no home
        :return: True if homed, False otherwise
        """
        # move x axis to limit switch
        timer = time.time()
        while not GPIO.input(self.x_endstop) == GPIO.HIGH:
            if time.time()-timer > timeout:
                print('X home timed out.')
                self.x_axis.disable()
                return False

            self.x_axis.step(-1)
            time.sleep(1/(self.default_speed * self.x_axis.steps_per_mm))

        print('im here first')
        self.x_axis.move(backoff_mm, self.default_speed)
        print('im here')
        self.x_position = 0
        return True

    def home_y_axis(self, timeout: int = 10, backoff_mm: int = -2) -> bool:
        """
        Homes y axis
        :param timeout: default number of seconds before timing out with no home
        :return: True if homed, False otherwise
        """
        # move y axis to limit switch
        timer = time.time()
        while not GPIO.input(self.y_endstop) == GPIO.HIGH:
            if time.time() - timer > timeout:
                print('Y home timed out.')
                self.y_axis.disable()
                return False

            self.y_axis.step(-1)
            time.sleep(1 / (self.default_speed * self.y_axis.steps_per_mm))

        self.y_axis.move(backoff_mm, self.default_speed)
        self.y_position = 0
        return True

    def home_all(self) -> bool:
        """
        Homes both x and y axes. Returns true if homed successfully
        :return: True if homed, False if an axis fails
        """
        print('Homing all axes...')
        if self.home_x_axis():
            if self.home_y_axis():
                return True
            else:
                return False
        else:
            return False

    def x_y_move(self, dx: float, dy: float, speed: int, min_delay: float = 0.01):
        """
        Moves x and y stepper motors linearly a
        distance dx and dy respectively, at speed
        speed, which is total speed over the distance
        d = sqrt(dx^2 + dy^2)
        :param dy: distance to move in y (can be negative)
        :param dx: distance to move in x (can be negative)
        :param speed: speed in mm/s over whole line
        :param min_delay: minimum delay time between loops
        :return: None
        """
        if dx > 0:
            dir_x = 1
        elif dx < 0:
            dir_x = -1
        else:
            dir_x = 0

        if dy > 0:
            dir_y = 1
        elif dy < 0:
            dir_y = -1
        else:
            dir_y = 0

        # Calculate total distance to move and number of iterations needed
        # to get there
        d = np.sqrt(dx ** 2 + dy ** 2)
        runtime = d / speed
        iterations = int(np.round(runtime / min_delay))
        if iterations == 0:
            print('Movement too small')
            return

        # Calculate number of steps needed to go in x and y
        steps_x = int(abs(dx) * self.x_axis.steps_per_mm)
        steps_y = int(abs(dy) * self.y_axis.steps_per_mm)

        # Divide those steps into each loop iteration
        steps_x_per_iter = int(np.round(steps_x / iterations))
        steps_y_per_iter = int(np.round(steps_y / iterations))

        # Within the loop iteration, interlace x and y steps using lcm of step counts
        if steps_x_per_iter > 0 and steps_y_per_iter > 0:
            iter_lcm = np.lcm(steps_x_per_iter, steps_y_per_iter)
            x_mod = iter_lcm // steps_x_per_iter
            y_mod = iter_lcm // steps_y_per_iter
        elif steps_x_per_iter == 0:
            iter_lcm = steps_y_per_iter
            x_mod = 0.1  # will never trigger
            y_mod = 1
        elif steps_y_per_iter == 0:
            iter_lcm = steps_x_per_iter
            x_mod = 1
            y_mod = 0.1  # will never trigger
        else:
            iter_lcm = 0
            x_mod = 1
            y_mod = 1

        # loop through each iteration in the move
        for i in range(iterations):
            # loop through lcm
            for j in np.arange(1, iter_lcm + 1, 1):
                step_x = j % x_mod == 0
                step_y = j % y_mod == 0
                if step_x and step_y:
                    self.x_axis.step(dir_x)
                    self.y_axis.step(dir_y)
                elif step_x:
                    self.x_axis.step(dir_x)
                elif step_y:
                    self.y_axis.step(dir_y)
                else:
                    pass
            time.sleep(min_delay)

        return

    def go_to_location(self, go_to: np.ndarray, speed: int):
        """
        Goes to a location [x,y] using the x_y_move function.
        Updates board's location after moving
        :param go_to: [x,y] coordinates to move to
        :param speed: speed at which to move
        :return: None
        """
        delta = go_to - self.location
        self.x_y_move(delta[0], delta[1], speed)
        self.location = go_to
        return

    def draw(self, coordinates: np.ndarray, speed: int):
        """
        Draws based on an array of coordinates of the format:
            [[x1, y1],
             [x2, y2],
             ...
             [xn, yn]]
        Using the go_to_location function.
        :param coordinates: Coordinates of format [[x1, y1], ...[xn, yn]]
        :param speed: speed at which to move
        :return: None
        """
        moves = len(coordinates)
        for i in range(moves):
            self.go_to_location(coordinates[i, :], speed)
        return

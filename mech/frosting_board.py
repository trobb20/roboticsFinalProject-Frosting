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
        x_steps_per_mm = 1
        y_steps_per_mm = 1
        self.default_speed = 20
        x_endstop_pin = 23  # GPIO23
        y_endstop_pin = 24  # GPIO24

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
        GPIO.setup(x_endstop_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.x_endstop = GPIO.input(x_endstop_pin)
        GPIO.setup(y_endstop_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.y_endstop = GPIO.input(y_endstop_pin)

    def home_x_axis(self, timeout: int = 10, backoff_mm: int = -2) -> bool:
        """
        Homes x axis
        :timeout: default number of seconds before timing out with no home
        :return: True if homed, False otherwise
        """
        # move x axis to limit switch
        timer = time.time()
        while not self.x_endstop == GPIO.HIGH:
            if time.time()-timer > timeout:
                print('X home timed out.')
                self.x_axis.disable()
                return False

            self.x_axis.step(-1)
            time.sleep(1/(self.default_speed * self.x_axis.steps_per_mm))

        self.x_axis.move(backoff_mm, self.default_speed)
        self.x_position = 0
        return True

    def home_y_axis(self, timeout: int = 10, backoff_mm: int = -2) -> bool:
        """
        Homes y axis
        :timeout: default number of seconds before timing out with no home
        :return: True if homed, False otherwise
        """
        # move y axis to limit switch
        timer = time.time()
        while not self.y_endstop == GPIO.HIGH:
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

    def x_y_move(self, dx: float, dy: float, speed: int):
        """
        Moves x and y stepper motors linearly a
        distance dx and dy respectively, at speed
        speed, which is total speed over the distance
        d = sqrt(dx^2 + dy^2)
        :param dy: distance to move in y (can be negative)
        :param dx: distance to move in x (can be negative)
        :param speed: speed in mm/s over whole line
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

        d = np.sqrt(dx**2 + dy**2)
        runtime = d / speed

        steps_x = int(abs(dx) * self.x_axis.steps_per_mm)
        steps_y = int(abs(dy) * self.y_axis.steps_per_mm)

        steps_lcm = np.lcm(steps_x, steps_y)
        delay = runtime / steps_lcm

        for i in range(steps_lcm):
            if i % (steps_lcm / steps_x) == 0 and i % (steps_lcm / steps_y) == 0:
                # step both x and y
                self.x_axis.step(dir_x)
                self.y_axis.step(dir_y)
            elif i % (steps_lcm / steps_x) == 0:
                # step x
                self.x_axis.step(dir_x)
            elif i % (steps_lcm / steps_y) == 0:
                # step y
                self.y_axis.step(dir_y)
            else:
                # don't step, just pause
                pass
            time.sleep(delay)

        return

    def go_to_location(self, go_to: np.ndarray) -> np.ndarray:
        # Move to an array of x, y based on our location
        delta = self.location - go_to
        self.x_y_move(delta[0], delta[1], self.default_speed)
        return self.location + delta

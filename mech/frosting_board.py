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
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import numpy as np


class FrostingMainBoard:
    def __init__(self):
        # Parameters
        x_steps_per_mm = 1
        y_steps_per_mm = 1
        self.default_speed = 20
        x_endstop_pin = 23 # GPIO23
        y_endstop_pin = 24 # GPIO24

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

    def home_x_axis(self):
        """
        Homes x axis
        :return:
        """
        # move x axis to limit switch

    def home_y_axis(self):
        """
        Homes y axis
        :return:
        """
        # move y axis to limit switch

    def go_to_location(self, location):
        # Move to an array of x, y based on our location

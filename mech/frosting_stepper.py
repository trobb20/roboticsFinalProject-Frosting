# ME35 FROSTING MECHANISM TEAM FINAL PROJECT
# NECESSARY FOR USE:
# sudo pip3 install adafruit-circuitpython-motorkit
# https://docs.circuitpython.org/projects/motorkit/en/latest/#
# sudo pip3 install adafruit-circuitpython-motor
# https://docs.circuitpython.org/projects/motor/en/latest/index.html


from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import time


class FrostingStepper:
    def __init__(self, kit: MotorKit, motor_number: int, steps_per_mm: float):
        """
        Constructs a frosting stepper
        :param kit: Adafruit MotorKit object. This is the board from which the steppers are controlled
        :param motor_number: Stepper number 1 or 2
        :param steps_per_mm: Number of mm traveled per step on the stepper
        """
        self.kit = kit
        self.motor_number = motor_number
        self.steps_per_mm = steps_per_mm

        # Setting actual stepper objects from motor_number
        if self.motor_number == 1:
            self.stepper_object = self.kit.stepper1
        elif self.motor_number == 2:
            self.stepper_object = self.kit.stepper2
        else:
            print('Defaulting to stepper #1 as stepper number not recognized.')
            self.stepper_object = self.kit.stepper1

    def move(self, dist: float, speed: float):
        """
        Moves a motor dist mm at speed mm/s
        :param dist: Distance in mm, can be negative
        :param speed: Speed in mm/s to move at
        :return: None
        """
        steps = int(dist * self.steps_per_mm)   # number of steps to move
        delay = 1/(speed * self.steps_per_mm)   # seconds per step
        if dist < 0:
            direction = stepper.BACKWARD
        elif dist > 0:
            direction = stepper.FORWARD
        else:
            print('Stepper not moving either direction')
            return

        for i in range(steps):
            self.stepper_object.onestep(direction=direction, style=stepper.DOUBLE)
            time.sleep(delay)

        return

    def disable(self):
        self.stepper_object.release()
        return

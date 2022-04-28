# ME35: Robotics Final Project
# Teddy Robbins, Tufts University 2022.
#
# frosting_motors.py
#
# These objects are used for controlling the stepper motors and
# dc motors required to move and extrude frosting.
#
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

    def step(self, dir: int):
        """
        Steps the motor one step, in either 1 (positive) or -1 (negative) direction
        :param dir: 1 for forward, -1 for reverse
        :return:
        """
        if dir < 0:
            direction = stepper.BACKWARD
        elif dir > 0:
            direction = stepper.FORWARD
        else:
            print('Stepper not moving either direction')
            return

        self.stepper_object.onestep(direction=direction, style=stepper.INTERLEAVE)
        return

    def move(self, dist: float, speed: float):
        """
        Moves a motor dist mm at speed mm/s. Blocking while moving
        :param dist: Distance in mm, can be negative
        :param speed: Speed in mm/s to move at
        :return: None
        """
        steps = int(abs(dist) * self.steps_per_mm)   # number of steps to move
        delay = 1/(speed * self.steps_per_mm)   # seconds per step
        if dist < 0:
            direction = stepper.BACKWARD
        elif dist > 0:
            direction = stepper.FORWARD
        else:
            print('Stepper not moving either direction')
            return

        for i in range(steps):
            self.stepper_object.onestep(direction=direction, style=stepper.INTERLEAVE)
            time.sleep(delay)

        return

    def disable(self):
        self.stepper_object.release()
        return


class FrostingDCMotor:
    def __init__(self, kit: MotorKit, motor_number: int, extrude_modifier: float = 1):
        """
        Constructs a frosting dc motor
        :param kit: Adafruit MotorKit object. This is the board from which the steppers are controlled
        :param motor_number: DC motor number 1, 2, 3 or 4.
        :param extrude_modifier: Modifies any drive() command by this value.
                                 Ex: drive(1 * extrude_modifier)
        """
        self.extrude_modifier = extrude_modifier
        self.kit = kit
        self.motor_number = motor_number

        # Setting actual motor objects from motor_number
        if self.motor_number == 1:
            self.motor_object = self.kit.motor1
        elif self.motor_number == 2:
            self.motor_object = self.kit.motor2
        elif self.motor_number == 3:
            self.motor_object = self.kit.motor3
        elif self.motor_number == 4:
            self.motor_object = self.kit.motor4
        else:
            print('Defaulting to motor #1 as motor number not recognized.')
            self.motor_object = self.kit.motor1

    def drive(self, dc: float):
        """
        Drive the motor at duty cycle dc. Negative values make the motor go backwards.
        :param dc: duty cycle from -1 to 1
        :return: None
        """
        drive_value = dc * self.extrude_modifier
        # Cap the dc
        if drive_value > 1:
            drive_value = 1
        elif drive_value < -1:
            drive_value = -1
        elif drive_value == 0:
            self.stop()
            return

        self.motor_object.throttle = drive_value
        return

    def stop(self):
        self.motor_object.throttle = 0
        return

    def coast(self):
        self.motor_object.throttle = None
        return

    def reset(self, reset_time: float = 6):
        """
        Resets the motor back to its starting position based on a reset_time
        :param reset_time: default tested with 0.6 modifier
        :return: None
        """
        start = time.time()
        self.drive(-1)
        while time.time() - start < reset_time:
            pass
        self.stop()
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

        self.stepper_object.onestep(direction=direction, style=stepper.MICROSTEP)
        return

    def move(self, dist: float, speed: float):
        """
        Moves a motor dist mm at speed mm/s. Blocking while moving
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
            self.stepper_object.onestep(direction=direction, style=stepper.MICROSTEP)
            time.sleep(delay)

        return

    def disable(self):
        self.stepper_object.release()
        return


class FrostingDCMotor:
    def __init__(self, kit: MotorKit, motor_number: int):
        """
        Constructs a frosting dc motor
        :param kit: Adafruit MotorKit object. This is the board from which the steppers are controlled
        :param motor_number: DC motor number 1, 2, 3 or 4.
        """
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
        :param dc: duty cycle from -100% to 100%
        :return: None
        """
        # Cap the dc
        if dc > 100:
            dc = 100
        elif dc < -100:
            dc = -100
        elif dc == 0:
            self.stop()
            return

        self.motor_object.throttle = dc/100
        return

    def stop(self):
        self.motor_object.throttle = 0
        return

    def coast(self):
        self.motor_object.throttle = None
        return

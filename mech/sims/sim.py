# Spaghetti code for simulating motor movement

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

# data logging
global bigListX, bigListY, iterListX, iterListY
bigListX = []
bigListY = []


def x_y_move(loc: np.ndarray, dx: float, dy: float, x_steps_per_mm, y_steps_per_mm):
    """
    Moves x and y stepper motors linearly a
    distance dx and dy respectively, at speed
    speed, which is total speed over the distance
    d = sqrt(dx^2 + dy^2)
    :param dy: distance to move in y (can be negative)
    :param dx: distance to move in x (can be negative)
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

    # Calculate number of steps needed to go in x and y
    steps_x = int(abs(dx) * x_steps_per_mm)
    steps_y = int(abs(dy) * y_steps_per_mm)

    # Within the loop iteration, interlace x and y steps using lcm of step counts
    if steps_x > 0 and steps_y > 0:
        iter_lcm = np.lcm(steps_x, steps_y)
        x_mod = iter_lcm // steps_x
        y_mod = iter_lcm // steps_y
    elif steps_x == 0:
        iter_lcm = steps_y
        x_mod = 0.1  # will never trigger
        y_mod = 1
    elif steps_y == 0:
        iter_lcm = steps_x
        x_mod = 1
        y_mod = 0.1  # will never trigger
    else:
        iter_lcm = 0
        x_mod = 1
        y_mod = 1

    print('On this move with, dx: %s, dy: %s' % (str(dx), str(dy)))
    print(' steps x, y ## %d %d steps/iter x, y ##'
          % (steps_x, steps_y))

    for j in np.arange(1, iter_lcm + 1, 1):
        step_x = j % x_mod == 0
        step_y = j % y_mod == 0
        if step_x and step_y:
            loc[0] = loc[0] + (dir_x / x_steps_per_mm)
            loc[1] = loc[1] + (dir_y / y_steps_per_mm)
        elif step_x:
            loc[0] = loc[0] + (dir_x / x_steps_per_mm)
        elif step_y:
            loc[1] = loc[1] + (dir_y / y_steps_per_mm)
        else:
            pass
        bigListX.append(loc[0])
        bigListY.append(loc[1])

    return loc


def funny_sin(x):
    return 15 * np.sin(0.2 * x) + x


def exponential(x):
    return 100 * (1 - np.e ** (-x / 30))


def spiral(theta):
    return 10 * theta


def sim_frosting(path: np.ndarray, x_steps_per_mm: int, y_steps_per_mm: int):
    pos = np.empty(np.shape(path))
    loc = np.zeros(2)
    pos[0, :] = loc

    # Simulation loop
    for i in range(len(pos)):
        dx = path[i, 0] - loc[0]
        dy = path[i, 1] - loc[1]
        new_loc = x_y_move(loc, dx, dy, x_steps_per_mm, y_steps_per_mm)
        pos[i, :] = new_loc
        loc = new_loc

    # Data processing and plotting
    num = [i for i in range(len(path))]
    err = [np.sqrt((path[i, 0] - pos[i, 0]) ** 2 + (path[i, 1] - pos[i, 1]) ** 2) for i in range(len(path))]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
    fig.set_size_inches(12, 4)

    ax1.plot(path[:, 0], path[:, 1])
    ax1.plot(pos[:, 0], pos[:, 1])
    ax1.set_title('Stepper desired path vs simulation: %s steps/mm' % str(x_steps_per_mm))
    ax1.set_xlabel('X position (mm)')
    ax1.set_ylabel('Y position (mm)')
    ax1.legend(['desired path', 'Simulated result'])

    ax2.plot(bigListX, bigListY, color='k')
    ax2.set_title('Steps on Path')
    ax2.set_xlabel('X position (mm)')
    ax2.set_ylabel('Y position (mm)')
    ax2.legend(['Individual Steps', 'Loop Iterations'])

    ax3.set_title('Error vs movement')
    ax3.set_xlabel('Movement #')
    ax3.set_ylabel('Absolute error (mm)')
    ax3.plot(num, err, 'r')
    plt.show()


# Testing

# Polar
# theta = np.linspace(0.1, 2 * np.pi, 50)
# r = spiral(theta)
# X = r * np.cos(theta)
# Y = r * np.sin(theta)

# Cartesian
# X = np.linspace(0.1, 100, 10)
# Y = exponential(X)

# Path
# path = np.array([X, Y]).T
# path = np.array(([0, 0],
#                     [50, 0],
#                     [50, 50],
#                     [0, 50],
#                     [0, 0]))

path = pd.read_csv('coordinates.csv').values[:, 0:2]
# flips and orients commands in bottom left
path = path * -1
path = path - np.array((np.min(path[:, 0]), np.min(path[:, 1])))

sim_frosting(path, 25, 25)

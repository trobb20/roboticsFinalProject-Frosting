# Spaghetti code for simulating motor movement

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from main.img_processing import run as run_img_processing


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

    stepsX = []
    stepsY = []

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
        stepsX.append(loc[0])
        stepsY.append(loc[1])

    return loc, stepsX, stepsY


def sim_frosting(path: np.ndarray, x_steps_per_mm: int, y_steps_per_mm: int):
    pos = np.empty(np.shape(path))
    loc = np.zeros(2)
    pos[0, :] = loc

    stepsX_all = []
    stepsY_all = []

    # Simulation loop
    for i in range(len(pos)):
        dx = path[i, 0] - loc[0]
        dy = path[i, 1] - loc[1]
        new_loc, stepsX, stepsY = x_y_move(loc, dx, dy, x_steps_per_mm, y_steps_per_mm)
        pos[i, :] = new_loc
        loc = new_loc
        stepsX_all = stepsX_all + stepsX
        stepsY_all = stepsY_all + stepsY

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

    ax2.plot(stepsX_all, stepsY_all, color='k')
    ax2.set_title('Steps on Path')
    ax2.set_xlabel('X position (mm)')
    ax2.set_ylabel('Y position (mm)')
    ax2.legend(['Individual Steps', 'Loop Iterations'])

    ax3.set_title('Error vs movement')
    ax3.set_xlabel('Movement #')
    ax3.set_ylabel('Absolute error (mm)')
    ax3.plot(num, err, 'r')
    plt.show()


def main():
    steps_per_mm = 10

    run_img_processing()
    path = pd.read_csv('bgd_coordinates.csv').values[:, 0:2]
    path2 = pd.read_csv('img_coordinates.csv').values[:, 0:2]

    # reorient
    path = path * -1
    path = path - np.array((np.min(path[:, 0]), np.min(path[:, 1])))
    path2 = path2 * -1
    path2 = path2 - np.array((np.min(path2[:, 0]), np.min(path2[:, 1])))

    sim_frosting(path, steps_per_mm, steps_per_mm)
    sim_frosting(path2, steps_per_mm, steps_per_mm)


if __name__ == '__main__':
    main()

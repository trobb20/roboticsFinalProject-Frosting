# For simulating motor movement

import numpy as np
import matplotlib.pyplot as plt
import time

# data logging
global bigListX, bigListY, iterListX, iterListY
bigListX = []
bigListY = []
iterListX = []
iterListY = []

def x_y_move(loc: np.ndarray, dx: float, dy: float, speed: int, min_delay: float = 0.01):
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

    d = np.sqrt(dx ** 2 + dy ** 2)
    runtime = d / speed
    iterations = int(np.round(runtime / min_delay))
    if iterations == 0:
        print('Movement too small')
        return loc

    steps_x = int(abs(dx) * x_steps_per_mm)
    steps_y = int(abs(dy) * y_steps_per_mm)

    steps_x_per_iter = int(np.round(steps_x / iterations))
    steps_y_per_iter = int(np.round(steps_y / iterations))

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

    print('On this move with dx: %s, dy: %s' % (str(dx), str(dy)))
    print('## %d iterations ## %d %d steps x, y ## %d %d steps/iter x, y ##'
          % (iterations, steps_x, steps_y, steps_x_per_iter, steps_y_per_iter))

    for i in range(iterations):
        # New way
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
        iterListX.append(loc[0])
        iterListY.append(loc[1])
        # old way
        # for j in range(steps_x_per_iter):
        #     loc[0] = loc[0] + (dir_x / x_steps_per_mm)
        #     plt.scatter(loc[0], loc[1], marker='o', color='b')
        # for k in range(steps_y_per_iter):
        #     loc[1] = loc[1] + (dir_y / y_steps_per_mm)
        #     plt.scatter(loc[0], loc[1], marker='o', color='b')
        # time.sleep(min_delay)

    return loc


def funny_sin(x):
    return 15 * np.sin(0.2 * x) + x


def exponential(x):
    return 100 * (1 - np.e ** (-x / 30))


def spiral(theta):
    return 10 * theta

# Testing

# Polar
theta = np.linspace(0.1, 4 * np.pi, 50)
r = spiral(theta)
X = r * np.cos(theta)
Y = r * np.sin(theta)

# Cartesian
# X = np.linspace(0.1, 100, 10)
# Y = exponential(X)

# Path
des = np.array([X, Y]).T
pos = np.empty(np.shape(des))
loc = np.zeros(2)
pos[0, :] = loc

# Movement params
speed = 50
x_steps_per_mm = 25
y_steps_per_mm = x_steps_per_mm

# Simulation loop
for i in range(len(pos)):
    dx = des[i, 0] - loc[0]
    dy = des[i, 1] - loc[1]
    new_loc = x_y_move(loc, dx, dy, speed, min_delay=.01)
    pos[i, :] = new_loc
    loc = new_loc

# Data processing and plotting
num = [i for i in range(len(des))]
err = [np.sqrt((des[i, 0] - pos[i, 0]) ** 2 + (des[i, 1] - pos[i, 1]) ** 2) for i in range(len(des))]

fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
fig.set_size_inches(12, 4)

ax1.plot(des[:, 0], des[:, 1])
ax1.plot(pos[:, 0], pos[:, 1])
ax1.set_title('Stepper desired path vs simulation: %s steps/mm' % str(x_steps_per_mm))
ax1.set_xlabel('X position (mm)')
ax1.set_ylabel('Y position (mm)')
ax1.legend(['Desired path', 'Simulated result'])

ax2.plot(bigListX, bigListY, color='k')
ax2.scatter(iterListX, iterListY, marker='o', color='g')
ax2.set_title('Steps + Loop Iterations on Path')
ax2.set_xlabel('X position (mm)')
ax2.set_ylabel('Y position (mm)')
ax2.legend(['Individual Steps', 'Loop Iterations'])

ax3.set_title('Error vs movement')
ax3.set_xlabel('Movement #')
ax3.set_ylabel('Absolute error (mm)')
ax3.plot(num, err, 'r')
plt.show()

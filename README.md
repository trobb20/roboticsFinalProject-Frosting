# ME35 Frosting Robot Code

Code for controlling the [frosting robot](https://www.youtube.com/watch?v=ddX_Plyb1gU) created in ME35 in the spring of 2022 by the students in ME35. 

### Programmed in Python3, this codebase:

1. Gets an image from airtable
2. Parses it into an array of coordinates for the robot to follow
3. Instructs the robot to follow the coordinates and extrude frosting onto the cake

### Scripts:

- `sim.py`
  - Simulates the robot movement
- `img_processing.py`
  - Gets the image and returns the coordinates
- `frosting_main.py`
  - controls the robot
- `frosting_board.py`
  - contains the object for the methods and properties required for controlling the robot
- `frosting_motors.py`
  - contains the objects for using the adafruit motor controller boards

### Contributers:

- Teddy R.
- Caroline H.
- Megan J.
- Jennifer L.


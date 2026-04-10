from random import choice
import turtle
import time

def task_func(colors):
    """
    Draws five squares of random colors using Turtle Graphics. Each square is drawn
    sequentially with a 1-second pause between squares.
    The function requires a list of colors as input and sets up a Turtle Graphics window, 
    creates a Turtle object, and uses it to draw the squares with colors from the provided list.
    The window remains open after drawing.

    Parameters:
        colors (list): A list of color names (as strings) to use for drawing the squares.

    Returns:
        None.

    Requirements:
    - random.choice
    - turtle
    - time

    Examples:
    >>> task_func(['red', 'blue', 'green', 'yellow', 'purple'])  # This will open a Turtle Graphics window and draw squares
    >>> turtle.TurtleScreen._RUNNING
    True  # Check if the Turtle Graphics screen is running
    """
    screen = turtle.Screen()
    screen.title("BigCodeBench 220 - Drawing Squares")
    t = turtle.Turtle()
    t.speed(1)

    for color in colors:
        t.color(color)
        t.begin_fill()
        for _
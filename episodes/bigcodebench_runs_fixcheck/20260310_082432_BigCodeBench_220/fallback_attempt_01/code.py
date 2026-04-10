from random import choice
import turtle
import time

def task_func(colors):
    turtle.setup(400, 400)
    t = turtle.Turtle()
    for _ in range(5):
        color = choice(colors)
        t.fillcolor(color)
        t.begin_fill()
        for _ in range(4):
            t.forward(100)
            t.right(90)
        t.end_fill()
        time.sleep(1)
    turtle.done()
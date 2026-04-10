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

import unittest
from unittest.mock import patch, call
import turtle
class TestCases(unittest.TestCase):
    @patch('turtle.Turtle')
    @patch('turtle.Screen')
    def test_turtle_setup(self, mock_screen, mock_turtle):
        """ Test the setup of the Turtle Graphics environment. """
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        task_func(colors)
        mock_screen.assert_called_once()
        mock_turtle.assert_called_once()
    @patch('turtle.Turtle')
    @patch('turtle.Screen')
    def test_function_executes_without_error(self, mock_screen, mock_turtle):
        """ Test that the task_func function executes without raising any errors. """
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        try:
            task_func(colors)
            execution_successful = True
        except Exception:
            execution_successful = False
        self.assertTrue(execution_successful)
    @patch('turtle.Turtle')
    def test_square_drawing(self, mock_turtle):
        """ Test that the turtle moves correctly to draw squares. """
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        task_func(colors)
        move_calls = [call.forward(100), call.right(90)] * 4 * 5  # 4 sides per square, 5 squares
        mock_turtle.return_value.assert_has_calls(move_calls, any_order=True)
    @patch('time.sleep')
    @patch('turtle.Turtle')
    def test_time_delay(self, mock_turtle, mock_sleep):
        """ Test that there is a time delay between each square. """
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        task_func(colors)
        self.assertEqual(mock_sleep.call_count, 5)
        mock_sleep.assert_called_with(1)
    @patch('turtle.Turtle')
    @patch('turtle.Screen')
    def test_mainloop_invocation(self, mock_screen, mock_turtle):
        """ Test that the Turtle window's mainloop is called. """
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        task_func(colors)
        mock_screen.return_value.mainloop.assert_called_once()

if __name__ == '__main__':
    import unittest
    unittest.main()

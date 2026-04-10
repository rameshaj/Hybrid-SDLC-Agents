LOGFILE_PATH = "logfile.log"

import subprocess
import time
import json
import platform

def task_func(interval, duration):
    if interval <= 0 or duration <= 0:
        raise ValueError("Both interval and duration must be greater than zero.")
    
    cpu_usage_data = []
    end_time = time.time() + duration
    
    while time.time() < end_time:
        if platform.system() == "Windows":
            cpu_usage = subprocess.check_output("wmic cpu get loadpercentage", shell=True)
            cpu_usage = int(cpu_usage.decode().split('\n')[1].strip())
        else:
            cpu_usage = subprocess.check_output("top -bn1 | grep 'Cpu(s)'", shell=True)
            cpu_usage = 100 - float(cpu_usage.decode().split(',')[3].split()[0])
        
        timestamp = time.time()
        cpu_usage_data.append({"timestamp": timestamp, "cpu_usage": cpu_usage})
        
        time.sleep(interval)
    
    try:
        with open(LOGFILE_PATH, 'w') as logfile:
            json.dump(cpu_usage_data, logfile)
    except IOError:
        return None
    
    return LOGFILE_PATH

import unittest
import os
import json
from unittest.mock import patch
class TestCases(unittest.TestCase):
    """Test cases for task_func."""
    def setUp(self):
        """
        Setup before each test case.
        """
        self.logfile_path = "logfile.log"
    def tearDown(self):
        """
        Cleanup after each test case.
        """
        if os.path.exists(self.logfile_path):
            os.remove(self.logfile_path)
    @patch("time.time")
    def test_normal_operation(self, mock_time):
        """
        Test the normal operation of the function.
        It should create a log file with the expected content.
        """
        # Create an iterator that starts at 0 and increments by 5 every time it's called
        time_iter = iter(range(0, 100, 5))
        mock_time.side_effect = lambda: next(time_iter)
        result = task_func(5, 25)
        self.assertEqual(result, self.logfile_path)
        self.assertTrue(os.path.exists(self.logfile_path))
    def test_invalid_interval(self):
        """
        Test the function with an invalid interval value (less than or equal to zero).
        It should raise a ValueError.
        """
        with self.assertRaises(ValueError):
            task_func(-1, 10)
    def test_invalid_duration(self):
        """
        Test the function with an invalid duration value (less than or equal to zero).
        It should raise a ValueError.
        """
        with self.assertRaises(ValueError):
            task_func(5, -10)
    @patch("subprocess.check_output")
    @patch("time.time")
    @patch("platform.system")
    def test_subprocess_output_handling_windows(
        self, mock_platform, mock_time, mock_subprocess
    ):
        """
        Test handling of subprocess output on Windows.
        It should correctly parse the CPU usage from the subprocess output.
        """
        mock_platform.return_value = "Windows"
        mock_time.side_effect = iter(range(0, 100, 5))
        mock_output = b'"\\Processor(_Total)\\% Processor Time","5.0"\n\n"2023-04-01 12:34:56.789","5.0"\n'
        mock_subprocess.return_value = mock_output
        result = task_func(5, 10)
        self.assertEqual(result, self.logfile_path)
    @patch("subprocess.check_output")
    @patch("time.time")
    @patch("platform.system")
    def test_subprocess_output_handling_linux(
        self, mock_platform, mock_time, mock_subprocess
    ):
        """
        Test handling of subprocess output on Linux.
        It should correctly parse the CPU usage from the subprocess output.
        """
        mock_platform.return_value = "Linux"
        mock_time.side_effect = iter(range(0, 100, 5))
        mock_output = b"Linux 4.15.0-54-generic (ubuntu) \nTasks: 195 total...\n%Cpu(s):  5.0 us,  2.0 sy,  0.0 ni, 92.0 id,  0.0 wa,  0.0 hi,  1.0 si,  0.0 st\n"
        mock_subprocess.return_value = mock_output
        result = task_func(5, 10)
        self.assertEqual(result, self.logfile_path)
    @patch("builtins.open", side_effect=IOError("Mocked error"))
    def test_io_error_handling(self, mock_open):
        """
        Test the function's behavior when an IOError occurs during file operations.
        It should handle the error and return None.
        """
        result = task_func(5, 10)
        self.assertIsNone(result)

if __name__ == '__main__':
    import unittest
    unittest.main()

import subprocess
import os
import signal
import time

def task_func(process_name: str) -> int:
    pids = subprocess.check_output(["pgrep", process_name]).decode().strip().split()
    count = 0
    for pid in pids:
        os.kill(int(pid), signal.SIGTERM)
        count += 1
    time.sleep(1)
    return count

import unittest
from unittest.mock import patch
import doctest
class TestCases(unittest.TestCase):
    @patch('subprocess.check_output')
    @patch('os.kill')
    def test_case_1(self, mock_os_kill, mock_subprocess_check_output):
        # Mock the subprocess output to simulate 3 processes with the name 'python'
        mock_subprocess_check_output.return_value = b'1234\n5678\n91011\n'
        
        result = task_func('python')
        self.assertEqual(result, 3)
    @patch('subprocess.check_output')
    @patch('os.kill')
    def test_case_2(self, mock_os_kill, mock_subprocess_check_output):
        # Mock the subprocess output to simulate no processes with the name 'java'
        mock_subprocess_check_output.return_value = b''
        
        result = task_func('java')
        self.assertEqual(result, 0)
    @patch('subprocess.check_output')
    @patch('os.kill')
    def test_case_3(self, mock_os_kill, mock_subprocess_check_output):
        # Mock the subprocess output to simulate 2 processes with the name 'node'
        mock_subprocess_check_output.return_value = b'1234\n5678\n'
        
        result = task_func('node')
        self.assertEqual(result, 2)
    @patch('subprocess.check_output')
    @patch('os.kill')
    def test_case_4(self, mock_os_kill, mock_subprocess_check_output):
        # Mock the subprocess output to simulate 1 process with the name 'ruby'
        mock_subprocess_check_output.return_value = b'1234\n'
        
        result = task_func('ruby')
        self.assertEqual(result, 1)
    @patch('subprocess.check_output')
    @patch('os.kill')
    def test_case_5(self, mock_os_kill, mock_subprocess_check_output):
        # Mock the subprocess output to simulate 4 processes with the name 'go'
        mock_subprocess_check_output.return_value = b'1234\n5678\n91011\n1213\n'
        
        result = task_func('go')
        self.assertEqual(result, 4)

if __name__ == '__main__':
    import unittest
    unittest.main()

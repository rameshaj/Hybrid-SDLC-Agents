from itertools import combinations
import math

def task_func(x, w):
    max_weight = float('-inf')
    max_substr = ''
    
    for i in range(len(x)):
        current_weight = 0
        current_substr = x[i]
        
        for j in range(i + 1, len(x)):
            current_weight += w[x[j]]
            current_substr += x[j]
            
            if current_weight > max_weight:
                max_weight = current_weight
                max_substr = current_substr
    
    return max_substr

import unittest
class TestCases(unittest.TestCase):
    def test_case_1(self):
        self.assertEqual(task_func('c', {'a': 1, 'b': 2, 'c': 3}), 'c')
    
    def test_case_2(self):
        self.assertEqual(task_func('aabc', {'a': 10, 'b': -5, 'c': 3}), 'aa')
    def test_case_3(self):
        self.assertEqual(task_func('aabc', {'a': 10, 'b': -2, 'c': 3}), 'aabc')
    def test_case_4(self):
        self.assertEqual(task_func('aabc', {'a': 2, 'b': -5, 'c': 3}), 'aa')
    
    def test_case_5(self):
        self.assertEqual(task_func('aabc', {'a': 0, 'b': -1, 'c': 1}), 'c')

if __name__ == '__main__':
    import unittest
    unittest.main()

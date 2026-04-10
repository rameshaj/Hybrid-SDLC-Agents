import itertools
import math

def task_func(x):
    max_sum = float('-inf')
    best_pair = None
    
    for key1, key2 in itertools.combinations(x.keys(), 2):
        sum_cosines = math.cos(x[key1]) + math.cos(x[key2])
        if sum_cosines > max_sum:
            max_sum = sum_cosines
            best_pair = (key1, key2)
    
    return best_pair

import unittest
class TestCases(unittest.TestCase):
    def test_case_1(self):
        self.assertEqual(sorted(task_func({'a': 1, 'b': 2, 'c': 3})), sorted(('a', 'b')))
    
    def test_case_2(self):
        self.assertEqual(sorted(task_func({'a': 1, 'b': 2, 'c': 3, 'd': 4})), sorted(('a', 'b')))
    def test_case_3(self):
        self.assertEqual( sorted(task_func({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})),  sorted(('e', 'a')))
    def test_case_4(self):
        self.assertEqual( sorted(task_func({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6})),  sorted(('f', 'a')))
    def test_case_5(self):
        self.assertEqual( sorted(task_func({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7})),  sorted(('g', 'f')))

if __name__ == '__main__':
    import unittest
    unittest.main()

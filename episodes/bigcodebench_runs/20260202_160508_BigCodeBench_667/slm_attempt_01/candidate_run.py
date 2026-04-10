def task_func(x, n):
    return [letter for letter, _ in heapq.nlargest(n, x.items(), key=lambda item: item[1])]

import unittest
class TestCases(unittest.TestCase):
    def test_case_1(self):
        self.assertEqual(task_func({'a': 1, 'b': 2, 'c': 3}, 2), ['c', 'b'])
    def test_case_2(self):
        self.assertEqual(task_func({'a': 1, 'b': 2, 'c': 3}, 1), ['c'])
    def test_case_3(self):
        self.assertEqual(task_func({'a': 1, 'b': 2, 'c': 3}, 3), ['c', 'b', 'a'])
    def test_case_4(self):
        self.assertEqual(task_func({'a': 1, 'b': 2, 'c': 3}, 0), [])
    def test_case_5(self):
        self.assertEqual(task_func({'a': 1, 'b': 2, 'c': 3}, 4), ['c', 'b', 'a'])

if __name__ == '__main__':
    import unittest
    unittest.main()

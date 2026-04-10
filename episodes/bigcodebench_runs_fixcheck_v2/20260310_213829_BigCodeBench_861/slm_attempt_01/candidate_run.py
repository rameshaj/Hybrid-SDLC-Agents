# Constants
POSSIBLE_ITEMS = ['apple', 'banana', 'cherry', 'date', 'elderberry']

from collections import Counter
from random import choice, seed

def task_func(list_of_lists):
    """
    Create a "shopping cart" (Counter object) for each list in list_of_lists. 
    The items in the cart are randomly selected from a predefined list of possible items (POSSIBLE_ITEMS).
    The frequency of each item in the cart corresponds to the length of the list.

    Parameters:
    - list_of_lists (list): A list of lists, each representing a 'basket'.

    Returns:
    - baskets (list): A list of Counters, each representing a 'shopping cart'.

    Requirements:
    - collections
    - random

    Example:
    >>> baskets = task_func([[1, 2, 3], [4, 5]])
    >>> all(isinstance(basket, Counter) for basket in baskets) # Illustrative, actual items will vary due to randomness
    True
    >>> sum(len(basket) for basket in baskets) # The sum of lengths of all baskets; illustrative example
    3
    """
    baskets = []
    for basket in list_of_lists:
        seed(42)  # For reproducibility, you can set a seed here
        item_counts = Counter(choice(POSSIBLE_ITEMS) for _ in range(len(basket)))
        baskets.append(item_counts)
    return baskets

import unittest
from collections import Counter
class TestCases(unittest.TestCase):
    def test_case_1(self):
        # Testing with empty list
        result = task_func([])
        self.assertEqual(result, [])
    def test_case_2(self):
        # Testing with empty sublists
        result = task_func([[], [], []])
        for basket in result:
            self.assertEqual(basket, Counter())
        
    def test_case_3(self):
        # Testing with sublists of different lengths
        result = task_func([[1], [1, 2], [1, 2, 3]])
        self.assertEqual(len(result), 3)
        self.assertEqual(sum(result[0].values()), 1)
        self.assertEqual(sum(result[1].values()), 2)
        self.assertEqual(sum(result[2].values()), 3)
    def test_case_4(self):
        # Testing with sublists containing the same element
        result = task_func([[1, 1, 1], [2, 2, 2, 2]])
        self.assertEqual(len(result), 2)
        self.assertEqual(sum(result[0].values()), 3)
        self.assertEqual(sum(result[1].values()), 4)
        
    def test_case_5(self):
        # Testing with large sublists
        result = task_func([[1]*100, [2]*200])
        self.assertEqual(len(result), 2)
        self.assertEqual(sum(result[0].values()), 100)
        self.assertEqual(sum(result[1].values()), 200)

if __name__ == '__main__':
    import unittest
    unittest.main()

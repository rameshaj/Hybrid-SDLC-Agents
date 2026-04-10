#CONSTANT
ANIMAL = ['cat', 'camel', 'cow', 'dog', 'elephant', 'fox', 'giraffe', 'hippo', 'iguana', 'jaguar']

from collections import Counter
from operator import itemgetter
import itertools

def task_func(animal_dict):
    valid_animals = {k: v for k, v in animal_dict.items() if k in ANIMAL}
    letter_counts = Counter(itertools.chain.from_iterable(valid_animals.keys()))
    sorted_counts = dict(sorted(letter_counts.items(), key=itemgetter(1), reverse=True))
    return sorted_counts

import unittest
from collections import Counter
class TestCases(unittest.TestCase):
    def test_case_1(self):
        # Input: A dictionary with multiple animal names and their initial letters.
        animal_dict = {'cat': 'c', 'dog': 'd', 'elephant': 'e', 'fox': 'f'}
        expected_output = dict(Counter('catdogelephantfox'))
        self.assertDictEqual(task_func(animal_dict), expected_output)
    def test_case_2(self):
        # Input: An empty dictionary.
        animal_dict = {}
        expected_output = {}
        self.assertDictEqual(task_func(animal_dict), expected_output)
    def test_case_3(self):
        # Input: A dictionary with one animal name and its initial letter.
        animal_dict = {'cat': 'c'}
        expected_output = {'c': 1, 'a': 1, 't': 1}
        self.assertDictEqual(task_func(animal_dict), expected_output)
    def test_case_4(self):
        # Input: A dictionary with animal names having repetitive initial letters.
        animal_dict = {'cat': 'c', 'camel': 'c', 'cow': 'c'}
        expected_output = dict(Counter('catcamelcow'))
        self.assertDictEqual(task_func(animal_dict), expected_output)
    def test_case_5(self):
        # Input: A dictionary with non-animal words and their initial letters.
        animal_dict = {'hello': 'h', 'world': 'w'}
        expected_output = {}
        self.assertDictEqual(task_func(animal_dict), expected_output)

if __name__ == '__main__':
    import unittest
    unittest.main()

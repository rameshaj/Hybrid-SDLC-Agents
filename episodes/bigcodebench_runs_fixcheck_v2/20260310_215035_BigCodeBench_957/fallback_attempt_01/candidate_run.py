import string
import re

def task_func(text: str) -> tuple:
    words = re.findall(r'\S+', text)
    num_words = len(words)
    cleaned_text = re.sub(r'[\s' + re.escape(string.punctuation) + ']', '', text)
    num_characters = len(cleaned_text)
    num_unique_characters = len(set(cleaned_text))
    return num_words, num_characters, num_unique_characters

import unittest
class TestCases(unittest.TestCase):
    def test_case_1(self):
        # Test simple text without any punctuation.
        result = task_func("Hello world")
        self.assertEqual(result, (2, 10, 7))
    def test_case_2(self):
        # Test simple text that includes punctuation.
        result = task_func("Hello, world!")
        self.assertEqual(result, (2, 10, 7))
    def test_case_3(self):
        # Test single word and no punctuation.
        result = task_func("Hello")
        self.assertEqual(result, (1, 5, 4))
    def test_case_4(self):
        # Test single word that includes punctuation.
        result = task_func("Hello!")
        self.assertEqual(result, (1, 5, 4))
    def test_case_5(self):
        # Test empty string.
        result = task_func("")
        self.assertEqual(result, (0, 0, 0))
    def test_case_6(self):
        # Test text with numbers and punctuation.
        result = task_func("There are 4 numbers here: 1, 2, 3, and 4.")
        self.assertEqual(result, (10, 27, 15))
    def test_case_7(self):
        # Test text with only whitespace and punctuation.
        result = task_func("     , , !")
        self.assertEqual(result, (3, 0, 0))
    def test_case_8(self):
        # Test text with multiple spaces between words.
        result = task_func("Multiple    spaces    here")
        self.assertEqual(result, (3, 18, 12))
    def test_case_9(self):
        # Test a long text.
        long_text = "This is a longer text designed to test the function's ability to handle more complex input, including a variety of characters and spaces."
        result = task_func(long_text)
        self.assertEqual(result, (23, 112, 22))

if __name__ == '__main__':
    import unittest
    unittest.main()

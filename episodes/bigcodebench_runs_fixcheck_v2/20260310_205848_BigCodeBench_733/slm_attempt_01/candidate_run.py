import re
import string

def task_func(content):
    """Count the non-stop words in a sentence without the last word.

    Parameters:
    - content (str): The sentence to count non-stopwords from.

    Returns:
    - count (int): The count of non-stopwords.

    Requirements:
    - re
    - string

    Example:
    >>> task_func('this is an example content')
    1
    """
    # Remove punctuation and split the sentence into words
    words = re.sub(r'[^\w\s]', '', content).split()
    
    # Count non-stopwords (excluding the last word)
    count = len(words) - 1
    
    return count

import unittest
class TestCases(unittest.TestCase):
    def test_case_1(self):
        # Test with a mix of stopwords and non-stopwords
        self.assertEqual(task_func('this is an example content'), 1)
    def test_case_2(self):
        # Test with all stopwords except the last word
        self.assertEqual(task_func('this is an the of'), 0)
    def test_case_3(self):
        # Test with no stopwords
        self.assertEqual(task_func('example content programming'), 2)
    def test_case_4(self):
        # Test with punctuation
        self.assertEqual(task_func('example, content; programming, python.'), 3)
    def test_case_5(self):
        # Test with an empty string
        self.assertEqual(task_func(''), 0)
    def test_case_6(self):
        # Test with a single non-stopword
        self.assertEqual(task_func('content'), 0)
    def test_case_7(self):
        # Test with a single stopword
        self.assertEqual(task_func('the'), 0)
    def test_case_8(self):
        # Test with a mix and uppercase letters
        self.assertEqual(task_func('This IS an Example Content'), 1)

if __name__ == '__main__':
    import unittest
    unittest.main()

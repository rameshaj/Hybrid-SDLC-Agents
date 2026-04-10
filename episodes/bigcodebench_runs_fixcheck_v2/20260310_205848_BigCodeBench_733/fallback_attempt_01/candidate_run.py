import re
import string

def task_func(content):
    stop_words = set(['a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'theirs', 'he', 'him', 'his', 'she', 'her', 'hers', 'we', 'us', 'our', 'ours', 'you', 'your', 'yours'])
    words = re.findall(r'\b\w+\b', content.lower())
    if len(words) > 1:
        words = words[:-1]
    return sum(1 for word in words if word not in stop_words)

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

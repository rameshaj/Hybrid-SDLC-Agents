import itertools
import math

def task_func(x):
    """
    Find the key pair in a dictionary, x, which has the highest sum of the cosine of each of its values.

    Parameters:
    - x (dict): The dictionary of key-value pairs.

    Returns:
    - tuple: The pair of keys with the highest sum of the cosine of their values.

    Requirements:
    - itertools
    - math

    Example:
    >>> task_func({'a': 1, 'b': 2, 'c': 3})
    ('a', 'b')
    ('a', 'b')
    >>> task_func({'a': 1, 'b': 2, 'c': 3, 'd': 4})
    ('a', 'b')
    ('a', 'b')
    """
    max_sum = float('-inf')
    max_key_pair = None

    for key1, value1 in x.items():
        for key2, value2 in itertools.combinations(x.keys(), 2):
            if key1 != key2:
                sum_cosines = math.cos(value1) + math.cos(value2)
                if sum_cosines > max_sum:
                    max_sum = sum_cosines
                    max_key_pair = (key1, key2)

    return max_key_pair
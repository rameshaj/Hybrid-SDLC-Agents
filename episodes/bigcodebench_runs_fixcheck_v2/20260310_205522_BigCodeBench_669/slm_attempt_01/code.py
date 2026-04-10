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

    for keys in itertools.combinations(x.keys(), 2):
        sum_cosines = sum(math.cos(value) for value in x[keys])
        if sum_cosines > max_sum:
            max_sum = sum_cosines
            max_key_pair = keys

    return max_key_pair
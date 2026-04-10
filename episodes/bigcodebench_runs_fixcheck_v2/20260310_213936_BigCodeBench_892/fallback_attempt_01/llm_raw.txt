import random
from collections import Counter

def task_func(strings: list) -> dict:
    pattern_count = Counter()
    for string in strings:
        count = string.count('}')
        if count > 0:
            pattern_count[count] += 1
    return dict(pattern_count)
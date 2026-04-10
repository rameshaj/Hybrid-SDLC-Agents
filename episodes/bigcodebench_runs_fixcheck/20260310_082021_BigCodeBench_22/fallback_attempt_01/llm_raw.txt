import collections
from itertools import zip_longest
from random import choices

def task_func(l1, l2, K=10):
    combined = [item for pair in zip_longest(l1, l2) for item in pair if item is not None]
    sample = choices(combined, k=K)
    return collections.Counter(sample)
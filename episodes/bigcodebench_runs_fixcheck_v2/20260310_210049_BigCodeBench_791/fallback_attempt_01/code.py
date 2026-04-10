# Constants
ELEMENTS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

from collections import Counter
import random
from itertools import cycle

def task_func(l):
    random.shuffle(l)
    l = l[3:] + l[:3]
    cycled_elements = cycle(l)
    first_30_elements = [next(cycled_elements) for _ in range(30)]
    counter = Counter(first_30_elements)
    return counter
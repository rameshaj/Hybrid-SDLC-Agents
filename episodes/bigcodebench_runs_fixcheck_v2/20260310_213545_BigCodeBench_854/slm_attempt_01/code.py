from functools import reduce
from itertools import permutations
import math

def task_func(numbers):
    if not all(isinstance(num, int) for num in numbers):
        raise TypeError("numbers must be a list of integers")
    if any(num < 0 for num in numbers):
        raise ValueError("numbers must not contain negative values")

    perm = list(permutations(numbers))
    fac = [reduce(lambda x, y: x * y, map(math.factorial, p)) for p in perm]
    return fac, perm
from functools import reduce
from itertools import permutations
import math

def task_func(numbers):
    if not all(isinstance(num, int) for num in numbers):
        raise TypeError("numbers must be a list of integers")
    if any(num < 0 for num in numbers):
        raise ValueError("input numbers must be non-negative")

    def factorial_sum(perm):
        return reduce(lambda x, y: x * math.factorial(y), perm)

    permutations_list = list(permutations(numbers))
    factorial_sums_list = [factorial_sum(perm) for perm in permutations_list]

    return factorial_sums_list, permutations_list
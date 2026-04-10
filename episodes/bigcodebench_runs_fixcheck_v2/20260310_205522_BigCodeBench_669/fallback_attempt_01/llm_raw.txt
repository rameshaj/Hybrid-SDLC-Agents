import itertools
import math

def task_func(x):
    max_sum = float('-inf')
    best_pair = None
    
    for key1, key2 in itertools.combinations(x.keys(), 2):
        sum_cosines = math.cos(x[key1]) + math.cos(x[key2])
        if sum_cosines > max_sum:
            max_sum = sum_cosines
            best_pair = (key1, key2)
    
    return best_pair
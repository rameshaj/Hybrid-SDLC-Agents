from itertools import combinations
import math

def task_func(x, w):
    max_weight = float('-inf')
    max_substr = ""
    
    for i in range(len(x)):
        current_weight = 0
        current_substr = ""
        for j in range(i, len(x)):
            current_weight += w.get(x[j], 0)
            current_substr += x[j]
            if current_weight > max_weight:
                max_weight = current_weight
                max_substr = current_substr
                
    return max_substr
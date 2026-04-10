POSSIBLE_LETTERS = ['a', 'b', 'c']

import random
import string

def task_func(word):
    if not word.isalpha():
        raise ValueError("Input must only contain letters.")
    
    pairs = []
    for i in range(len(word) - 1):
        pairs.append(word[i:i+2])
    
    return pairs
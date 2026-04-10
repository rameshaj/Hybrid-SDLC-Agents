from collections import Counter
import random
import itertools

def task_func(length, count, seed=0):
    random.seed(seed)
    letters = ['a', 'b', 'c', 'd', 'e']
    if length <= 0 or count <= 0:
        return Counter()
    generated_strings = [''.join(random.choices(letters, k=length)) for _ in range(count)]
    letter_count = Counter(itertools.chain.from_iterable(generated_strings))
    return letter_count
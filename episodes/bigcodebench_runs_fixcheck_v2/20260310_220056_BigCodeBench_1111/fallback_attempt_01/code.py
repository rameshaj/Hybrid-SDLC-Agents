#CONSTANT
ANIMAL = ['cat', 'camel', 'cow', 'dog', 'elephant', 'fox', 'giraffe', 'hippo', 'iguana', 'jaguar']

from collections import Counter
from operator import itemgetter
import itertools

def task_func(animal_dict):
    valid_animals = {k: v for k, v in animal_dict.items() if k in ANIMAL}
    letter_counts = Counter()
    
    for letters in valid_animals.values():
        letter_counts.update(letters)
    
    sorted_counts = dict(sorted(letter_counts.items(), key=itemgetter(1), reverse=True))
    return sorted_counts
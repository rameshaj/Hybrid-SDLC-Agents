import random
import re

def task_func(text, seed=None):
    if seed is not None:
        random.seed(seed)

    def scramble_word(word):
        if len(word) > 3:
            scrambled = word[0] + ''.join(random.sample(word[1:-1], len(word)-2)) + word[-1]
            return scrambled
        return word

    return ' '.join(scramble_word(word) for word in re.findall(r'\b\w+\b', text))
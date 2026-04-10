import random
import re

def task_func(text, seed=None):
    if seed is not None:
        random.seed(seed)

    def scramble_word(word):
        if len(word) <= 3:
            return word
        middle = list(word[1:-1])
        random.shuffle(middle)
        return word[0] + ''.join(middle) + word[-1]

    words = re.findall(r'\b\w+\b', text)
    scrambled_words = [scramble_word(word) for word in words]
    
    for original, scrambled in zip(words, scrambled_words):
        text = text.replace(original, scrambled, 1)

    return text
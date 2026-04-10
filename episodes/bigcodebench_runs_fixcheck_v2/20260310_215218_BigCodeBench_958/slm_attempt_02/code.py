import random
import re

def task_func(text, seed=None):
    """
    Scramble the letters in each word of a given text, keeping the first and last letters of each word intact.

    Parameters:
    text (str): The text to be scrambled.
    seed (int, optional): A seed for the random number generator to ensure reproducible results.
                          Defaults to None (not set).

    Returns:
    str: The scrambled text.

    Requirements:
    - random
    - re

    Notes:
    - Words are determined by regex word boundaries.
    - The scrambling only affects words longer than three characters, leaving shorter words unchanged.

    Examples:
    >>> task_func('Hello, world!', 0)
    'Hello, wlrod!'
    >>> task_func("Programming is fun, isn't it?", 42)
    "Prmiangmrog is fun, isn't it?"
    """
    if seed is not None:
        random.seed(seed)

    scrambled_text = []
    for word in re.findall(r'\b\w+\b', text):
        if len(word) > 3:
            scrambled_word = list(word)
            scrambled_word[1:-1] = random.sample(scrambled_word[1:-1], len(scrambled_word[1:-1]))
            scrambled_text.append(''.join(scrambled_word))
        else:
            scrambled_text.append(word)

    return ' '.join(scrambled_text)
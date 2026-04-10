POSSIBLE_LETTERS = ['a', 'b', 'c']

import random
import string

def task_func(word):
    """
    Generates a list of random pairs of adjacent letters from the given word. The number of such pairs will be equal to the length of the constant POSSIBLE_LETTERS.
    
    Parameters:
    word (str): The input string. Must only contain letters.
    
    Returns:
    list: A list of random pairs of adjacent letters from the word. If the word has fewer than 2 letters, returns a list of empty strings based on POSSIBLE_LETTERS length.
    
    Requirements:
    - random
    - string
    
    Raises:
    ValueError: If the input contains non-letter characters.
    
    Examples:
    >>> random.seed(0)
    >>> task_func('abcdef')
    ['de', 'de', 'ab']
    >>> task_func('xyz')
    ['yz', 'yz', 'yz']
    """
    if not word.isalpha():
        raise ValueError("Input must only contain letters.")
    
    result = []
    for i in range(len(word) - 1):
        result.append(word[i:i+2])
    return result
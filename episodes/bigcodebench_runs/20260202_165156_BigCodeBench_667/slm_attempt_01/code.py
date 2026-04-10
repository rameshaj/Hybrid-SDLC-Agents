import heapq
import collections

def task_func(x, n):
    """
    Find the n most common letters in a dictionary, x, where the key letters and the values are their frequencies.

    Parameters:
    - x (dict): The dictionary of letter frequencies.
    - n (int): The number of most frequent letters to return.

    Returns:
    - list: The n most frequent letters.

    Requirements:
    - heapq
    - collections

    Example:
    >>> task_func({'a': 1, 'b': 2, 'c': 3}, 2)
    ['c', 'b']
    """
    # Count the frequency of each letter
    letter_counts = collections.Counter(x)
    
    # Use a heap to find the n most frequent letters
    most_common_letters = heapq.nlargest(n, letter_counts.items(), key=lambda item: item[1])
    
    # Extract the letters from the tuples in the heap
    result = [letter for letter, count in most_common_letters]
    
    return result
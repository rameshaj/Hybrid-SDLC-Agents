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
    letter_counts = collections.Counter(x)
    most_common_letters = letter_counts.most_common(n)
    return [letter for letter, count in most_common_letters]
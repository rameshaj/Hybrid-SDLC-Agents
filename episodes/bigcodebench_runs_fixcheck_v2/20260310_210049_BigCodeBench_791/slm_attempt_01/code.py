# Constants
ELEMENTS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

from collections import Counter
import random
from itertools import cycle

def task_func(l):
    """
    Create a counter from a list "l" and move the first 3 elements to the end of the list.

    Parameters:
    - l (list): A list of elements that the function will process. 

    Returns:
    - counter (collections.Counter): A frequency counter that maps elements from the input list to their frequencies in the first 30 elements of the cycled, shuffled list. 
    
    Requirements:
    - collections
    - random
    - itertools

    Example:
    >>> random.seed(42)
    >>> task_func(ELEMENTS)
    Counter({'I': 3, 'F': 3, 'G': 3, 'J': 3, 'E': 3, 'A': 3, 'B': 3, 'H': 3, 'D': 3, 'C': 3})
    """
    # Create a counter from the input list
    counter = Counter(l)
    
    # Shuffle the list and move the first 3 elements to the end
    shuffled_list = cycle(l)
    first_three_elements = [next(shuffled_list) for _ in range(3)]
    remaining_elements = [next(shuffled_list) for _ in range(len(l) - 3)]
    
    # Combine the shuffled list with the first three elements
    combined_list = first_three_elements + remaining_elements
    
    # Return the frequency counter of the combined list
    return Counter(combined_list)
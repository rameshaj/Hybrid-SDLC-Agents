import re
import string

def task_func(content):
    """Count the non-stop words in a sentence without the last word.

    Parameters:
    - content (str): The sentence to count non-stopwords from.

    Returns:
    - count (int): The count of non-stopwords.

    Requirements:
    - re
    - string

    Example:
    >>> task_func('this is an example content')
    1
    """
    # Remove punctuation and split the sentence into words
    words = re.sub(r'[^\w\s]', '', content).split()
    
    # Count non-stopwords (excluding the last word)
    count = len(words) - 1
    
    return count
from collections import defaultdict
import re

def task_func(word: str) -> dict:
    sanitized_word = re.sub(r'[^a-zA-Z]', '', word)
    counts = defaultdict(int)
    
    for i in range(len(sanitized_word) - 1):
        pair = sanitized_word[i:i+2]
        counts[pair] += 1
    
    return counts
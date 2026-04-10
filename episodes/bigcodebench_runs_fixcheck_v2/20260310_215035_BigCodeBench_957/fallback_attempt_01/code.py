import string
import re

def task_func(text: str) -> tuple:
    words = re.findall(r'\S+', text)
    num_words = len(words)
    cleaned_text = re.sub(r'[\s' + re.escape(string.punctuation) + ']', '', text)
    num_characters = len(cleaned_text)
    num_unique_characters = len(set(cleaned_text))
    return num_words, num_characters, num_unique_characters
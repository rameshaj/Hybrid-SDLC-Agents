import string
import re

def task_func(text: str) -> tuple:
    words = len(re.findall(r'\b\w+\b', text))
    characters = sum(1 for char in text if char.isalnum())
    unique_characters = len(set(text.replace(" ", "").replace(",", "").replace(".", "").replace("!", "").replace("?", "").replace("'", "").replace("\"", "")))
    return words, characters, unique_characters
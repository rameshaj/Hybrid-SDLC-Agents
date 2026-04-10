def task_func(sentence):
    words = re.findall(r'\b\w+\b', sentence.lower())
    return dict(Counter(words))
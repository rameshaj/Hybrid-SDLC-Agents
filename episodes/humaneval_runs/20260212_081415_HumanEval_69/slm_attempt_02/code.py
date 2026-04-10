def search(lst):
    from collections import Counter
    counter = Counter(lst)
    for num, freq in counter.items():
        if num <= freq and num > 0:
            return num
    return -1
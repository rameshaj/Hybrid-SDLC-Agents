def search(lst):
    from collections import Counter
    freq = Counter(lst)
    for num, count in freq.items():
        if num <= count and num > 0:
            return num
    return -1
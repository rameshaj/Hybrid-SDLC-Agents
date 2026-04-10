def search(lst):
    from collections import Counter
    count = Counter(lst)
    for num, freq in count.items():
        if num <= freq and num > 0:
            return num
    return -1
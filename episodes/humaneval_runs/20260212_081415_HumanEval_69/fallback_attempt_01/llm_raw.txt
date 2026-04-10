def search(lst):
    from collections import Counter
    count = Counter(lst)
    result = -1
    for num in count:
        if num > 0 and count[num] >= num:
            result = max(result, num)
    return result
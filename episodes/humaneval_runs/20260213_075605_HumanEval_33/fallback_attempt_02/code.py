def sort_third(l: list):
    sorted_third = sorted(l[i] for i in range(len(l)) if i % 3 == 0)
    result = l[:]
    for i in range(len(l)):
        if i % 3 == 0:
            result[i] = sorted_third.pop(0)
    return result
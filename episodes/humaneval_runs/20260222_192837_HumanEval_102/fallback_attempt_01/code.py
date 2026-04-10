def choose_num(x, y):
    if x > y:
        return -1
    start = int(y) if y % 2 == 0 else int(y) - 1
    for num in range(start, int(x) - 1, -2):
        if num % 2 == 0:
            return num
    return -1
def choose_num(x, y):
    if x % 2 != 0:
        x += 1
    if y % 2 != 0:
        y -= 1
    return max(x, y) if max(x, y) % 2 == 0 else -1
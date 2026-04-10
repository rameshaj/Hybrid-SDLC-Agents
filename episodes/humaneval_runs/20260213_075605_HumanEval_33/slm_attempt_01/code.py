def sort_third(l: list):
    return [x if i % 3 != 0 else sorted(x) for i, x in enumerate(l)]
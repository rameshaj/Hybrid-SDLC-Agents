def get_row(lst, x):
    return sorted([(i, j) for i, row in enumerate(lst) for j, val in enumerate(row) if val == x], key=lambda t: (t[0], -t[1]))
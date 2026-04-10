def f(x):
        return sum([coeff * x**i for i, coeff in enumerate(xs)])

    left, right = -1e6, 1e6
    while right - left > 1e-7:
        mid = (left + right) / 2
        if f(mid) == 0:
            return mid
        elif f(mid) * f(left) < 0:
            right = mid
        else:
            left = mid
    return (left + right) / 2
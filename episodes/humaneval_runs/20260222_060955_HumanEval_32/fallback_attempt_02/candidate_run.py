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



METADATA = {}


def check(candidate):
    import math
    import random
    rng = random.Random(42)
    import copy
    for _ in range(100):
        ncoeff = 2 * rng.randint(1, 4)
        coeffs = []
        for _ in range(ncoeff):
            coeff = rng.randint(-10, 10)
            if coeff == 0:
                coeff = 1
            coeffs.append(coeff)
        solution = candidate(copy.deepcopy(coeffs))
        assert math.fabs(poly(coeffs, solution)) < 1e-4



def __run_tests():
    check(globals().get('find_zero'))

if __name__ == '__main__':
    __run_tests()

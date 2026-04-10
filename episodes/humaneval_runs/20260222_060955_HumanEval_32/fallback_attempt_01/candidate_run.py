if len(xs) % 2 != 0 or xs[-1] == 0:
        raise ValueError("Invalid polynomial coefficients")

    def f(x):
        return poly(xs, x)

    def derivative(xs):
        return [i * xs[i] for i in range(1, len(xs))]

    def f_prime(x):
        return poly(derivative(xs), x)

    x = 0
    for _ in range(100):
        fx = f(x)
        if abs(fx) < 1e-7:
            return x
        fpx = f_prime(x)
        if fpx == 0:
            break
        x -= fx / fpx

    raise ValueError("Failed to find a zero")



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

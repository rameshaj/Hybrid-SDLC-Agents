def find_zero(xs: list):
    n = len(xs) - 1
    a = xs[n]
    b = xs[n - 1]
    c = xs[n - 2]
    
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return None
    
    root1 = (-b + math.sqrt(discriminant)) / (2*a)
    return root1



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

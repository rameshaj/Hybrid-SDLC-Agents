def find_zero(xs: list):
    if len(xs) % 2 != 0 or xs[-1] == 0:
        raise ValueError("Invalid input")
    
    # Find the largest non-zero coefficient
    max_coeff = max(xs)
    
    # Reduce the polynomial by dividing all coefficients by the largest non-zero coefficient
    xs = [coeff / max_coeff for coeff in xs]
    
    # Use the Newton-Raphson method to find a root of the polynomial
    x = 0.0
    while True:
        f_x = poly(xs, x)
        if abs(f_x) < 1e-6:
            return x
        df_x = sum([i * coeff * math.pow(x, i - 1) for i, coeff in enumerate(xs)])
        x -= f_x / df_x



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

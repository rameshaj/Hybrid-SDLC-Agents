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
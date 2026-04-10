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
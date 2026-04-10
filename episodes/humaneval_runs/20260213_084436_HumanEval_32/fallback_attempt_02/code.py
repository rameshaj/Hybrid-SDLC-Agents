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
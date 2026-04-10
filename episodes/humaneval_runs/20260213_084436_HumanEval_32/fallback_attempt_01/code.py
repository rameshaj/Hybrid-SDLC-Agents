def find_zero(xs: list):
    a = xs[-1]
    b = xs[-2]
    c = xs[-3] if len(xs) > 2 else 0
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return root1 if root1 != 0 else root2
    return None
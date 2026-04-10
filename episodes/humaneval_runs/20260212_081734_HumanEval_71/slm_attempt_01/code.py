def triangle_area(a, b, c):
    if a + b > c and a + c > b and b + c > a:
        return round((a * b * c) ** 0.5 / 4, 2)
    else:
        return -1
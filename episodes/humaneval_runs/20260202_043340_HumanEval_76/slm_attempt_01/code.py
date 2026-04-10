def is_simple_power(x, n):
    if n == 1:
        return x == 1
    if x < 1 or n < 2:
        return False
    while n <= x:
        if n == x:
            return True
        n *= n
    return False
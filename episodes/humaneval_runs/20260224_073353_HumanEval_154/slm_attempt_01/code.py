def cycpattern_check(a , b):
    if len(b) > len(a):
        return False
    for i in range(len(b)):
        rotated = b[i:] + b[:i]
        if rotated in a:
            return True
    return False
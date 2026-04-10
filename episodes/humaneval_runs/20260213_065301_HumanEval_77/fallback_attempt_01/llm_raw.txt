def iscube(a):
    if a < 0:
        a = -a
    return round(a ** (1/3)) ** 3 == a
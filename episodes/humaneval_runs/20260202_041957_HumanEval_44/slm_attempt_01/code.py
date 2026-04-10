def change_base(x: int, base: int):
    if base < 2 or base > 9:
        raise ValueError("Base must be between 2 and 9")
    
    result = ""
    while x > 0:
        result = str(x % base) + result
        x //= base
    
    return result
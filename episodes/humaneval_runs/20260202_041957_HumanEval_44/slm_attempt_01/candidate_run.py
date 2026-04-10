def change_base(x: int, base: int):
    if base < 2 or base > 9:
        raise ValueError("Base must be between 2 and 9")
    
    result = ""
    while x > 0:
        result = str(x % base) + result
        x //= base
    
    return result



METADATA = {}


def check(candidate):
    assert candidate(8, 3) == "22"
    assert candidate(9, 3) == "100"
    assert candidate(234, 2) == "11101010"
    assert candidate(16, 2) == "10000"
    assert candidate(8, 2) == "1000"
    assert candidate(7, 2) == "111"
    for x in range(2, 8):
        assert candidate(x, x + 1) == str(x)



def __run_tests():
    check(globals().get('change_base'))

if __name__ == '__main__':
    __run_tests()

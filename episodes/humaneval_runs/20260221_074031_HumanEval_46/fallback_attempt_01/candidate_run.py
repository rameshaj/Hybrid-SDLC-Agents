def fib4(n: int):
    if n == 0 or n == 1 or n == 3:
        return 0
    if n == 2:
        return 2
    
    a, b, c, d = 0, 0, 2, 0
    for _ in range(4, n + 1):
        a, b, c, d = b, c, d, a + b + c + d
    return d



METADATA = {}


def check(candidate):
    assert candidate(5) == 4
    assert candidate(8) == 28
    assert candidate(10) == 104
    assert candidate(12) == 386



def __run_tests():
    check(globals().get('fib4'))

if __name__ == '__main__':
    __run_tests()

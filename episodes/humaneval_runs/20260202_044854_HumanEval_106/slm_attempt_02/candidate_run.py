def f(n):
    return [i * (i + 1) // 2 if i % 2 else i for i in range(1, n + 1)]

def check(candidate):

    assert candidate(5) == [1, 2, 6, 24, 15]
    assert candidate(7) == [1, 2, 6, 24, 15, 720, 28]
    assert candidate(1) == [1]
    assert candidate(3) == [1, 2, 6]


def __run_tests():
    check(globals().get('f'))

if __name__ == '__main__':
    __run_tests()

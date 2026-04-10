def sum_to_n(n: int):
    return n * (n + 1) // 2



METADATA = {}


def check(candidate):
    assert candidate(1) == 1
    assert candidate(6) == 21
    assert candidate(11) == 66
    assert candidate(30) == 465
    assert candidate(100) == 5050



def __run_tests():
    check(globals().get('sum_to_n'))

if __name__ == '__main__':
    __run_tests()

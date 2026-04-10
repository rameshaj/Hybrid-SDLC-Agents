def greatest_common_divisor(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate(3, 7) == 1
    assert candidate(10, 15) == 5
    assert candidate(49, 14) == 7
    assert candidate(144, 60) == 12


def __run_tests():
    check(globals().get('greatest_common_divisor'))

if __name__ == '__main__':
    __run_tests()

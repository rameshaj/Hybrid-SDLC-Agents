def string_sequence(n: int) -> str:
    return ' '.join(map(str, range(n + 1)))



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate(0) == '0'
    assert candidate(3) == '0 1 2 3'
    assert candidate(10) == '0 1 2 3 4 5 6 7 8 9 10'


def __run_tests():
    check(globals().get('string_sequence'))

if __name__ == '__main__':
    __run_tests()

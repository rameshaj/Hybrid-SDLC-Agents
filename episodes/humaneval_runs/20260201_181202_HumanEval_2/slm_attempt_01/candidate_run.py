def truncate_number(number: float) -> float:
    return number - int(number)



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate(3.5) == 0.5
    assert abs(candidate(1.33) - 0.33) < 1e-6
    assert abs(candidate(123.456) - 0.456) < 1e-6


def __run_tests():
    check(globals().get('truncate_number'))

if __name__ == '__main__':
    __run_tests()

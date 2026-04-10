def sort_numbers(numbers: str) -> str:
    return ' '.join(sorted(numbers.split()))



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('') == ''
    assert candidate('three') == 'three'
    assert candidate('three five nine') == 'three five nine'
    assert candidate('five zero four seven nine eight') == 'zero four five seven eight nine'
    assert candidate('six five four three two one zero') == 'zero one two three four five six'


def __run_tests():
    check(globals().get('sort_numbers'))

if __name__ == '__main__':
    __run_tests()

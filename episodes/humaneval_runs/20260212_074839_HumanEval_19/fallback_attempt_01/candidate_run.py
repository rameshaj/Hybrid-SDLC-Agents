def sort_numbers(numbers: str) -> str:
    num_dict = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3,
        'four': 4, 'five': 5, 'six': 6, 'seven': 7,
        'eight': 8, 'nine': 9
    }
    sorted_numbers = sorted(numbers.split(), key=lambda x: num_dict[x])
    return ' '.join(sorted_numbers)



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

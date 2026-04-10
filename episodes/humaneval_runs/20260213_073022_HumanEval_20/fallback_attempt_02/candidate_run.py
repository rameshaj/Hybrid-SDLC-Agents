def find_closest_elements(numbers):
    numbers.sort()
    closest_pair = (numbers[0], numbers[1])
    min_diff = abs(numbers[1] - numbers[0])
    
    for i in range(1, len(numbers)):
        diff = abs(numbers[i] - numbers[i - 1])
        if diff < min_diff:
            min_diff = diff
            closest_pair = (numbers[i - 1], numbers[i])
    
    return closest_pair



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2]) == (3.9, 4.0)
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0]) == (5.0, 5.9)
    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.2]) == (2.0, 2.2)
    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0]) == (2.0, 2.0)
    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1]) == (2.2, 3.1)



def __run_tests():
    check(globals().get('find_closest_elements'))

if __name__ == '__main__':
    __run_tests()

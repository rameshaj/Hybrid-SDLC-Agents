def intersperse(numbers, delimeter):
    result = []
    for i, number in enumerate(numbers):
        result.append(number)
        if i < len(numbers) - 1:
            result.append(delimeter)
    return result



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate([], 7) == []
    assert candidate([5, 6, 3, 2], 8) == [5, 8, 6, 8, 3, 8, 2]
    assert candidate([2, 2, 2], 2) == [2, 2, 2, 2, 2]


def __run_tests():
    check(globals().get('intersperse'))

if __name__ == '__main__':
    __run_tests()

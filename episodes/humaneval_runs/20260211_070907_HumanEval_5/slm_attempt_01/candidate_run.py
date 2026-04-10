def intersperse(numbers: List[int], delimeter: int) -> List[int]:
    return [numbers[i] for i in range(len(numbers)) if i % 2 == 0] + [delimeter] + [numbers[i] for i in range(len(numbers)) if i % 2 != 0]



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

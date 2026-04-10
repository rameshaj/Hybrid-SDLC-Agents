def rolling_max(numbers: List[int]) -> List[int]:
    result = []
    current_max = float('-inf')
    for num in numbers:
        if num > current_max:
            current_max = num
        result.append(current_max)
    return result



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate([]) == []
    assert candidate([1, 2, 3, 4]) == [1, 2, 3, 4]
    assert candidate([4, 3, 2, 1]) == [4, 4, 4, 4]
    assert candidate([3, 2, 3, 100, 3]) == [3, 3, 3, 100, 100]


def __run_tests():
    check(globals().get('rolling_max'))

if __name__ == '__main__':
    __run_tests()

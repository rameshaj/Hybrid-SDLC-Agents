def filter_integers(values: List[Any]) -> List[int]:
    return [value for value in values if isinstance(value, int)]



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate([]) == []
    assert candidate([4, {}, [], 23.2, 9, 'adasd']) == [4, 9]
    assert candidate([3, 'c', 3, 3, 'a', 'b']) == [3, 3, 3]


def __run_tests():
    check(globals().get('filter_integers'))

if __name__ == '__main__':
    __run_tests()

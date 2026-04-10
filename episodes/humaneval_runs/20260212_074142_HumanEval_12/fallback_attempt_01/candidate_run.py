def longest(strings):
    if not strings:
        return None
    return max(strings, key=len)



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate([]) == None
    assert candidate(['x', 'y', 'z']) == 'x'
    assert candidate(['x', 'yyy', 'zzzz', 'www', 'kkkk', 'abc']) == 'zzzz'


def __run_tests():
    check(globals().get('longest'))

if __name__ == '__main__':
    __run_tests()

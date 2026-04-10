def max_element(l: list):
    return max(l)



METADATA = {}


def check(candidate):
    assert candidate([1, 2, 3]) == 3
    assert candidate([5, 3, -5, 2, -3, 3, 9, 0, 124, 1, -10]) == 124


def __run_tests():
    check(globals().get('max_element'))

if __name__ == '__main__':
    __run_tests()

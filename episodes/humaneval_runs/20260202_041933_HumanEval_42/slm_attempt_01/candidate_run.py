def incr_list(l: list):
    return [x + 1 for x in l]



METADATA = {}


def check(candidate):
    assert candidate([]) == []
    assert candidate([3, 2, 1]) == [4, 3, 2]
    assert candidate([5, 2, 5, 2, 3, 3, 9, 0, 123]) == [6, 3, 6, 3, 4, 4, 10, 1, 124]



def __run_tests():
    check(globals().get('incr_list'))

if __name__ == '__main__':
    __run_tests()

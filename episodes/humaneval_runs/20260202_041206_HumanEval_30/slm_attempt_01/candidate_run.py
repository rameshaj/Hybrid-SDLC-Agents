def get_positive(l: list):
    return [x for x in l if x > 0]



METADATA = {}


def check(candidate):
    assert candidate([-1, -2, 4, 5, 6]) == [4, 5, 6]
    assert candidate([5, 3, -5, 2, 3, 3, 9, 0, 123, 1, -10]) == [5, 3, 2, 3, 3, 9, 123, 1]
    assert candidate([-1, -2]) == []
    assert candidate([]) == []



def __run_tests():
    check(globals().get('get_positive'))

if __name__ == '__main__':
    __run_tests()

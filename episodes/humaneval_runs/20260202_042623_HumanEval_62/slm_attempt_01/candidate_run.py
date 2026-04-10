def derivative(xs: list):
    return [i * xs[i] for i in range(1, len(xs))]



METADATA = {}


def check(candidate):
    assert candidate([3, 1, 2, 4, 5]) == [1, 4, 12, 20]
    assert candidate([1, 2, 3]) == [2, 6]
    assert candidate([3, 2, 1]) == [2, 2]
    assert candidate([3, 2, 1, 0, 4]) == [2, 2, 0, 16]
    assert candidate([1]) == []



def __run_tests():
    check(globals().get('derivative'))

if __name__ == '__main__':
    __run_tests()

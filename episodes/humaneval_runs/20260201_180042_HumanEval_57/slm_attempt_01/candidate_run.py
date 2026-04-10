def monotonic(l: list):
    return all(x <= y for x, y in zip(l, l[1:])) or all(x >= y for x, y in zip(l, l[1:]))



METADATA = {}


def check(candidate):
    assert candidate([1, 2, 4, 10]) == True
    assert candidate([1, 2, 4, 20]) == True
    assert candidate([1, 20, 4, 10]) == False
    assert candidate([4, 1, 0, -10]) == True
    assert candidate([4, 1, 1, 0]) == True
    assert candidate([1, 2, 3, 2, 5, 60]) == False
    assert candidate([1, 2, 3, 4, 5, 60]) == True
    assert candidate([9, 9, 9, 9]) == True



def __run_tests():
    check(globals().get('monotonic'))

if __name__ == '__main__':
    __run_tests()

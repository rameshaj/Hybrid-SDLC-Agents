def below_threshold(l: list, t: int):
    return all(x < t for x in l)



METADATA = {}


def check(candidate):
    assert candidate([1, 2, 4, 10], 100)
    assert not candidate([1, 20, 4, 10], 5)
    assert candidate([1, 20, 4, 10], 21)
    assert candidate([1, 20, 4, 10], 22)
    assert candidate([1, 8, 4, 10], 11)
    assert not candidate([1, 8, 4, 10], 10)



def __run_tests():
    check(globals().get('below_threshold'))

if __name__ == '__main__':
    __run_tests()

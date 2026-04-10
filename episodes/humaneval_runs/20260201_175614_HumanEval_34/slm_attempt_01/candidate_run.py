def unique(l: list):
    return sorted(set(l))



METADATA = {}


def check(candidate):
    assert candidate([5, 3, 5, 2, 3, 3, 9, 0, 123]) == [0, 2, 3, 5, 9, 123]



def __run_tests():
    check(globals().get('unique'))

if __name__ == '__main__':
    __run_tests()

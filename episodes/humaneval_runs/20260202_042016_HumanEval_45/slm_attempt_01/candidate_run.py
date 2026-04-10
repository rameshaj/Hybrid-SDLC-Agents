def triangle_area(a, h):
    return (a * h) / 2



METADATA = {}


def check(candidate):
    assert candidate(5, 3) == 7.5
    assert candidate(2, 2) == 2.0
    assert candidate(10, 8) == 40.0



def __run_tests():
    check(globals().get('triangle_area'))

if __name__ == '__main__':
    __run_tests()

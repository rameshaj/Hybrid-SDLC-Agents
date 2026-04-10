def sort_even(l: list):
    even_indices = [i for i in range(len(l)) if i % 2 == 0]
    return [even_indices[i] if i % 2 == 0 else sorted(l[i]) for i in range(len(l))]



METADATA = {}


def check(candidate):
    assert tuple(candidate([1, 2, 3])) == tuple([1, 2, 3])
    assert tuple(candidate([5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10])) == tuple([-10, 3, -5, 2, -3, 3, 5, 0, 9, 1, 123])
    assert tuple(candidate([5, 8, -12, 4, 23, 2, 3, 11, 12, -10])) == tuple([-12, 8, 3, 4, 5, 2, 12, 11, 23, -10])



def __run_tests():
    check(globals().get('sort_even'))

if __name__ == '__main__':
    __run_tests()

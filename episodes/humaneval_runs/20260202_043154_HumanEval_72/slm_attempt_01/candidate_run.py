def will_it_fly(q, w):
    return q == q[::-1] and sum(q) <= w

def check(candidate):

    # Check some simple cases
    assert candidate([3, 2, 3], 9) is True
    assert candidate([1, 2], 5) is False
    assert candidate([3], 5) is True
    assert candidate([3, 2, 3], 1) is False


    # Check some edge cases that are easy to work out by hand.
    assert candidate([1, 2, 3], 6) is False
    assert candidate([5], 5) is True



def __run_tests():
    check(globals().get('will_it_fly'))

if __name__ == '__main__':
    __run_tests()

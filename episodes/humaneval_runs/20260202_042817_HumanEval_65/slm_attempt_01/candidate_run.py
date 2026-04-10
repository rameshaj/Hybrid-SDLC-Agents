def circular_shift(x, shift):
    if shift > len(str(x)):
        return str(x)[::-1]
    else:
        return str(x)[-shift:] + str(x[:-shift])

def check(candidate):

    # Check some simple cases
    assert candidate(100, 2) == "001"
    assert candidate(12, 2) == "12"
    assert candidate(97, 8) == "79"
    assert candidate(12, 1) == "21", "This prints if this assert fails 1 (good for debugging!)"

    # Check some edge cases that are easy to work out by hand.
    assert candidate(11, 101) == "11", "This prints if this assert fails 2 (also good for debugging!)"



def __run_tests():
    check(globals().get('circular_shift'))

if __name__ == '__main__':
    __run_tests()

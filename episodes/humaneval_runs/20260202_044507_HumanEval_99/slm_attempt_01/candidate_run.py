def closest_integer(value):
    num = float(value)
    if num > 0:
        return int(num + 0.5)
    else:
        return int(num - 0.5)

def check(candidate):

    # Check some simple cases
    assert candidate("10") == 10, "Test 1"
    assert candidate("14.5") == 15, "Test 2"
    assert candidate("-15.5") == -16, "Test 3"
    assert candidate("15.3") == 15, "Test 3"

    # Check some edge cases that are easy to work out by hand.
    assert candidate("0") == 0, "Test 0"



def __run_tests():
    check(globals().get('closest_integer'))

if __name__ == '__main__':
    __run_tests()

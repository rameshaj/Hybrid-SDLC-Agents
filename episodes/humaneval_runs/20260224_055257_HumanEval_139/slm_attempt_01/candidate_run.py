def special_factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def check(candidate):

    # Check some simple cases
    assert candidate(4) == 288, "Test 4"
    assert candidate(5) == 34560, "Test 5"
    assert candidate(7) == 125411328000, "Test 7"

    # Check some edge cases that are easy to work out by hand.
    assert candidate(1) == 1, "Test 1"



def __run_tests():
    check(globals().get('special_factorial'))

if __name__ == '__main__':
    __run_tests()

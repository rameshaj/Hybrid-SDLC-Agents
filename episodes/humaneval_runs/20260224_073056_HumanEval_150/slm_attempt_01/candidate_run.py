def x_or_y(n, x, y):
    if n > 1:
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return y
        return x
    else:
        return y

def check(candidate):

    # Check some simple cases
    assert candidate(7, 34, 12) == 34
    assert candidate(15, 8, 5) == 5
    assert candidate(3, 33, 5212) == 33
    assert candidate(1259, 3, 52) == 3
    assert candidate(7919, -1, 12) == -1
    assert candidate(3609, 1245, 583) == 583
    assert candidate(91, 56, 129) == 129
    assert candidate(6, 34, 1234) == 1234
    

    # Check some edge cases that are easy to work out by hand.
    assert candidate(1, 2, 0) == 0
    assert candidate(2, 2, 0) == 2



def __run_tests():
    check(globals().get('x_or_y'))

if __name__ == '__main__':
    __run_tests()

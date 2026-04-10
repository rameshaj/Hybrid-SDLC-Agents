def is_equal_to_sum_even(n):
    return n % 2 == 0 and n >= 8

def check(candidate):
    assert candidate(4) == False
    assert candidate(6) == False
    assert candidate(8) == True
    assert candidate(10) == True
    assert candidate(11) == False
    assert candidate(12) == True
    assert candidate(13) == False
    assert candidate(16) == True


def __run_tests():
    check(globals().get('is_equal_to_sum_even'))

if __name__ == '__main__':
    __run_tests()

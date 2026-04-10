def choose_num(x, y):
    if x > y:
        return -1
    start = int(y) if y % 2 == 0 else int(y) - 1
    for num in range(start, int(x) - 1, -2):
        if num % 2 == 0:
            return num
    return -1

def check(candidate):

    # Check some simple cases
    assert candidate(12, 15) == 14
    assert candidate(13, 12) == -1
    assert candidate(33, 12354) == 12354
    assert candidate(5234, 5233) == -1
    assert candidate(6, 29) == 28
    assert candidate(27, 10) == -1

    # Check some edge cases that are easy to work out by hand.
    assert candidate(7, 7) == -1
    assert candidate(546, 546) == 546



def __run_tests():
    check(globals().get('choose_num'))

if __name__ == '__main__':
    __run_tests()

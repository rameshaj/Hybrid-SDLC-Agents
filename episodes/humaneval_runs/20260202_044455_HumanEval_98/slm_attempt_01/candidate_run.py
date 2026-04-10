def count_upper(s):
    return sum(1 for i, c in enumerate(s) if i % 2 == 0 and c in 'AEIOU')

def check(candidate):

    # Check some simple cases
    assert candidate('aBCdEf')  == 1
    assert candidate('abcdefg') == 0
    assert candidate('dBBE') == 0
    assert candidate('B')  == 0
    assert candidate('U')  == 1
    assert candidate('') == 0
    assert candidate('EEEE') == 2

    # Check some edge cases that are easy to work out by hand.
    assert True



def __run_tests():
    check(globals().get('count_upper'))

if __name__ == '__main__':
    __run_tests()

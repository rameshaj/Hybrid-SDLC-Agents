def simplify(x, n):
    def parse_fraction(fraction):
        numerator, denominator = map(int, fraction.split('/'))
        return numerator, denominator

    x_num, x_den = parse_fraction(x)
    n_num, n_den = parse_fraction(n)

    result_num = x_num * n_num
    result_den = x_den * n_den

    return result_num % result_den == 0

def check(candidate):

    # Check some simple cases
    assert candidate("1/5", "5/1") == True, 'test1'
    assert candidate("1/6", "2/1") == False, 'test2'
    assert candidate("5/1", "3/1") == True, 'test3'
    assert candidate("7/10", "10/2") == False, 'test4'
    assert candidate("2/10", "50/10") == True, 'test5'
    assert candidate("7/2", "4/2") == True, 'test6'
    assert candidate("11/6", "6/1") == True, 'test7'
    assert candidate("2/3", "5/2") == False, 'test8'
    assert candidate("5/2", "3/5") == False, 'test9'
    assert candidate("2/4", "8/4") == True, 'test10'


    # Check some edge cases that are easy to work out by hand.
    assert candidate("2/4", "4/2") == True, 'test11'
    assert candidate("1/5", "5/1") == True, 'test12'
    assert candidate("1/5", "1/5") == False, 'test13'



def __run_tests():
    check(globals().get('simplify'))

if __name__ == '__main__':
    __run_tests()

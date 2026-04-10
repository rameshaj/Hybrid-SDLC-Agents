def reverse_delete(s, c):
    result = ''.join(char for char in s if char not in c)
    is_palindrome = result == result[::-1]
    return result, is_palindrome

def check(candidate):

    assert candidate("abcde","ae") == ('bcd',False)
    assert candidate("abcdef", "b") == ('acdef',False)
    assert candidate("abcdedcba","ab") == ('cdedc',True)
    assert candidate("dwik","w") == ('dik',False)
    assert candidate("a","a") == ('',True)
    assert candidate("abcdedcba","") == ('abcdedcba',True)
    assert candidate("abcdedcba","v") == ('abcdedcba',True)
    assert candidate("vabba","v") == ('abba',True)
    assert candidate("mamma", "mia") == ("", True)


def __run_tests():
    check(globals().get('reverse_delete'))

if __name__ == '__main__':
    __run_tests()

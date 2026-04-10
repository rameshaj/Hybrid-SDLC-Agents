def digitSum(s):
    return sum(ord(c) for c in s if c.isupper())

def check(candidate):

    # Check some simple cases
    assert True, "This prints if this assert fails 1 (good for debugging!)"
    assert candidate("") == 0, "Error"
    assert candidate("abAB") == 131, "Error"
    assert candidate("abcCd") == 67, "Error"
    assert candidate("helloE") == 69, "Error"
    assert candidate("woArBld") == 131, "Error"
    assert candidate("aAaaaXa") == 153, "Error"

    # Check some edge cases that are easy to work out by hand.
    assert True, "This prints if this assert fails 2 (also good for debugging!)"
    assert candidate(" How are yOu?") == 151, "Error"
    assert candidate("You arE Very Smart") == 327, "Error"



def __run_tests():
    check(globals().get('digitSum'))

if __name__ == '__main__':
    __run_tests()

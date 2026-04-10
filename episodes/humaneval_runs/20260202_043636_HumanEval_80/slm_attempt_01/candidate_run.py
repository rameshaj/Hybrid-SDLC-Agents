def is_happy(s):
    return len(s) >= 3 and all(len(set(s[i:i+3])) == 3 for i in range(len(s)-2))

def check(candidate):

    # Check some simple cases
    assert candidate("a") == False , "a"
    assert candidate("aa") == False , "aa"
    assert candidate("abcd") == True , "abcd"
    assert candidate("aabb") == False , "aabb"
    assert candidate("adb") == True , "adb"
    assert candidate("xyy") == False , "xyy"
    assert candidate("iopaxpoi") == True , "iopaxpoi"
    assert candidate("iopaxioi") == False , "iopaxioi"


def __run_tests():
    check(globals().get('is_happy'))

if __name__ == '__main__':
    __run_tests()

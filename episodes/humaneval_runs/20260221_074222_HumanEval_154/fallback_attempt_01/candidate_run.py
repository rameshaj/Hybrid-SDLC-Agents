def cycpattern_check(a, b):
    if len(b) > len(a):
        return False
    b_rotations = [b[i:] + b[:i] for i in range(len(b))]
    return any(rotation in a for rotation in b_rotations)

def check(candidate):

    # Check some simple cases
    #assert True, "This prints if this assert fails 1 (good for debugging!)"

    # Check some edge cases that are easy to work out by hand.
    #assert True, "This prints if this assert fails 2 (also good for debugging!)"
    assert  candidate("xyzw","xyw") == False , "test #0"
    assert  candidate("yello","ell") == True , "test #1"
    assert  candidate("whattup","ptut") == False , "test #2"
    assert  candidate("efef","fee") == True , "test #3"
    assert  candidate("abab","aabb") == False , "test #4"
    assert  candidate("winemtt","tinem") == True , "test #5"



def __run_tests():
    check(globals().get('cycpattern_check'))

if __name__ == '__main__':
    __run_tests()

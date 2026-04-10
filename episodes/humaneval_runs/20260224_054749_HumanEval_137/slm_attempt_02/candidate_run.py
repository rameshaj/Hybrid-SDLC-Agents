def compare_one(a, b):
    if isinstance(a, str) and isinstance(b, str):
        a = float(a.replace(',', '.'))
        b = float(b.replace(',', '.'))
    
    if isinstance(a, float) and isinstance(b, float):
        return max(a, b)
    
    if isinstance(a, int) and isinstance(b, int):
        return max(a, b)
    
    return None

def check(candidate):

    # Check some simple cases
    assert candidate(1, 2) == 2
    assert candidate(1, 2.5) == 2.5
    assert candidate(2, 3) == 3
    assert candidate(5, 6) == 6
    assert candidate(1, "2,3") == "2,3"
    assert candidate("5,1", "6") == "6"
    assert candidate("1", "2") == "2"
    assert candidate("1", 1) == None

    # Check some edge cases that are easy to work out by hand.
    assert True



def __run_tests():
    check(globals().get('compare_one'))

if __name__ == '__main__':
    __run_tests()

def compare_one(a, b):
    def convert_to_float(value):
        if isinstance(value, str):
            return float(value.replace(',', '.'))
        return float(value)

    a_float = convert_to_float(a)
    b_float = convert_to_float(b)

    if a_float > b_float:
        return a
    elif b_float > a_float:
        return b
    else:
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

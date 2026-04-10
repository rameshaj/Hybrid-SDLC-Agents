def prod_signs(arr):
    if not arr:
        return None
    sign_product = 1
    for num in arr:
        if num == 0:
            return 0
        sign_product *= -1 if num < 0 else 1
    return sum(abs(num) * sign_product for num in arr)

def check(candidate):

    # Check some simple cases
    assert True, "This prints if this assert fails 1 (good for debugging!)"
    assert candidate([1, 2, 2, -4]) == -9
    assert candidate([0, 1]) == 0
    assert candidate([1, 1, 1, 2, 3, -1, 1]) == -10
    assert candidate([]) == None
    assert candidate([2, 4,1, 2, -1, -1, 9]) == 20
    assert candidate([-1, 1, -1, 1]) == 4
    assert candidate([-1, 1, 1, 1]) == -4
    assert candidate([-1, 1, 1, 0]) == 0

    # Check some edge cases that are easy to work out by hand.
    assert True, "This prints if this assert fails 2 (also good for debugging!)"



def __run_tests():
    check(globals().get('prod_signs'))

if __name__ == '__main__':
    __run_tests()

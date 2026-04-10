def exchange(lst1, lst2):
    odd_in_lst1 = any(x % 2 != 0 for x in lst1)
    even_in_lst2 = any(x % 2 == 0 for x in lst2)
    if odd_in_lst1 and even_in_lst2:
        return "YES"
    elif not odd_in_lst1:
        return "YES"
    else:
        return "NO"

def check(candidate):

    # Check some simple cases
    assert candidate([1, 2, 3, 4], [1, 2, 3, 4]) == "YES"
    assert candidate([1, 2, 3, 4], [1, 5, 3, 4]) == "NO"
    assert candidate([1, 2, 3, 4], [2, 1, 4, 3]) == "YES" 
    assert candidate([5, 7, 3], [2, 6, 4]) == "YES"
    assert candidate([5, 7, 3], [2, 6, 3]) == "NO" 
    assert candidate([3, 2, 6, 1, 8, 9], [3, 5, 5, 1, 1, 1]) == "NO"

    # Check some edge cases that are easy to work out by hand.
    assert candidate([100, 200], [200, 200]) == "YES"



def __run_tests():
    check(globals().get('exchange'))

if __name__ == '__main__':
    __run_tests()

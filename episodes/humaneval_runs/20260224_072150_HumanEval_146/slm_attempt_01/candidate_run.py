def specialFilter(nums):
    return sum(1 for num in nums if num > 10 and int(str(num)[0]) % 2 != 0 and int(str(num)[-1]) % 2 != 0)

def check(candidate):

    # Check some simple cases
    assert candidate([5, -2, 1, -5]) == 0  
    assert candidate([15, -73, 14, -15]) == 1
    assert candidate([33, -2, -3, 45, 21, 109]) == 2
    assert candidate([43, -12, 93, 125, 121, 109]) == 4
    assert candidate([71, -2, -33, 75, 21, 19]) == 3


    # Check some edge cases that are easy to work out by hand.
    assert candidate([1]) == 0              
    assert candidate([]) == 0                   



def __run_tests():
    check(globals().get('specialFilter'))

if __name__ == '__main__':
    __run_tests()

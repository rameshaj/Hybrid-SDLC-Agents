def by_length(arr):
    if not arr:
        return []
    
    # Filter and sort the array
    filtered_sorted = sorted([x for x in arr if 1 <= x <= 9])
    
    # Reverse the sorted array
    reversed_sorted = filtered_sorted[::-1]
    
    # Replace each digit with its corresponding name
    names = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    result = [names[i - 1] for i in reversed_sorted]
    
    return result

def check(candidate):

    # Check some simple cases
    assert True, "This prints if this assert fails 1 (good for debugging!)"
    assert candidate([2, 1, 1, 4, 5, 8, 2, 3]) == ["Eight", "Five", "Four", "Three", "Two", "Two", "One", "One"], "Error"
    assert candidate([]) == [], "Error"
    assert candidate([1, -1 , 55]) == ['One'], "Error"

    # Check some edge cases that are easy to work out by hand.
    assert True, "This prints if this assert fails 2 (also good for debugging!)"
    assert candidate([1, -1, 3, 2]) == ["Three", "Two", "One"]
    assert candidate([9, 4, 8]) == ["Nine", "Eight", "Four"]



def __run_tests():
    check(globals().get('by_length'))

if __name__ == '__main__':
    __run_tests()

def get_odd_collatz(n):
    if not isinstance(n, int) or n <= 0:
        raise ValueError("Input must be a positive integer")
    
    odd_numbers = []
    while n != 1:
        if n % 2 != 0:
            odd_numbers.append(n)
        n = (3 * n + 1) // 2
    
    return sorted(odd_numbers)

def check(candidate):

    # Check some simple cases
    assert candidate(14) == [1, 5, 7, 11, 13, 17]
    assert candidate(5) == [1, 5]
    assert candidate(12) == [1, 3, 5], "This prints if this assert fails 1 (good for debugging!)"

    # Check some edge cases that are easy to work out by hand.
    assert candidate(1) == [1], "This prints if this assert fails 2 (also good for debugging!)"



def __run_tests():
    check(globals().get('get_odd_collatz'))

if __name__ == '__main__':
    __run_tests()

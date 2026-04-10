def histogram(test):
    if not test:
        return {}
    
    letters = test.split()
    letter_counts = {}
    
    for letter in letters:
        if letter in letter_counts:
            letter_counts[letter] += 1
        else:
            letter_counts[letter] = 1
    
    max_count = max(letter_counts.values())
    result = {letter: count for letter, count in letter_counts.items() if count == max_count}
    
    return result

def check(candidate):

    # Check some simple cases
    assert candidate('a b b a') == {'a':2,'b': 2}, "This prints if this assert fails 1 (good for debugging!)"
    assert candidate('a b c a b') == {'a': 2, 'b': 2}, "This prints if this assert fails 2 (good for debugging!)"
    assert candidate('a b c d g') == {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'g': 1}, "This prints if this assert fails 3 (good for debugging!)"
    assert candidate('r t g') == {'r': 1,'t': 1,'g': 1}, "This prints if this assert fails 4 (good for debugging!)"
    assert candidate('b b b b a') == {'b': 4}, "This prints if this assert fails 5 (good for debugging!)"
    assert candidate('r t g') == {'r': 1,'t': 1,'g': 1}, "This prints if this assert fails 6 (good for debugging!)"
    
    
    # Check some edge cases that are easy to work out by hand.
    assert candidate('') == {}, "This prints if this assert fails 7 (also good for debugging!)"
    assert candidate('a') == {'a': 1}, "This prints if this assert fails 8 (also good for debugging!)"



def __run_tests():
    check(globals().get('histogram'))

if __name__ == '__main__':
    __run_tests()

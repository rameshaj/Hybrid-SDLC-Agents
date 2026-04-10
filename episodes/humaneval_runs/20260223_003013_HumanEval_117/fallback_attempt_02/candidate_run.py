def select_words(s, n):
    vowels = set('aeiouAEIOU')
    words = s.split()
    result = []
    for word in words:
        consonant_count = sum(1 for char in word if char.isalpha() and char not in vowels)
        if consonant_count == n:
            result.append(word)
    return result

def check(candidate):

    # Check some simple cases
    assert candidate("Mary had a little lamb", 4) == ["little"], "First test error: " + str(candidate("Mary had a little lamb", 4))      
    assert candidate("Mary had a little lamb", 3) == ["Mary", "lamb"], "Second test error: " + str(candidate("Mary had a little lamb", 3))  
    assert candidate("simple white space", 2) == [], "Third test error: " + str(candidate("simple white space", 2))      
    assert candidate("Hello world", 4) == ["world"], "Fourth test error: " + str(candidate("Hello world", 4))  
    assert candidate("Uncle sam", 3) == ["Uncle"], "Fifth test error: " + str(candidate("Uncle sam", 3))


    # Check some edge cases that are easy to work out by hand.
    assert candidate("", 4) == [], "1st edge test error: " + str(candidate("", 4))
    assert candidate("a b c d e f", 1) == ["b", "c", "d", "f"], "2nd edge test error: " + str(candidate("a b c d e f", 1))



def __run_tests():
    check(globals().get('select_words'))

if __name__ == '__main__':
    __run_tests()

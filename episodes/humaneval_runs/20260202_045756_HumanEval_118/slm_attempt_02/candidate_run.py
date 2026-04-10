def get_closest_vowel(word):
    vowels = 'aeiouAEIOU'
    for i in range(len(word) - 2, 0, -1):
        if word[i] in vowels and word[i + 1] not in vowels and word[i - 1] not in vowels:
            return word[i]
    return ''

def check(candidate):

    # Check some simple cases
    assert candidate("yogurt") == "u"
    assert candidate("full") == "u"
    assert candidate("easy") == ""
    assert candidate("eAsy") == ""
    assert candidate("ali") == ""
    assert candidate("bad") == "a"
    assert candidate("most") == "o"
    assert candidate("ab") == ""
    assert candidate("ba") == ""
    assert candidate("quick") == ""
    assert candidate("anime") == "i"
    assert candidate("Asia") == ""
    assert candidate("Above") == "o"

    # Check some edge cases that are easy to work out by hand.
    assert True



def __run_tests():
    check(globals().get('get_closest_vowel'))

if __name__ == '__main__':
    __run_tests()

def odd_count(lst):
    return ["the number of odd elements {}n the str{}ng {} of the {}nput.".format(len([x for x in lst[i] if int(x) % 2 != 0]), i+1, lst[i], i+1) for i in range(len(lst))]

def check(candidate):

    # Check some simple cases
    assert candidate(['1234567']) == ["the number of odd elements 4n the str4ng 4 of the 4nput."], "Test 1"
    assert candidate(['3',"11111111"]) == ["the number of odd elements 1n the str1ng 1 of the 1nput.", "the number of odd elements 8n the str8ng 8 of the 8nput."], "Test 2"
    assert candidate(['271', '137', '314']) == [
        'the number of odd elements 2n the str2ng 2 of the 2nput.',
        'the number of odd elements 3n the str3ng 3 of the 3nput.',
        'the number of odd elements 2n the str2ng 2 of the 2nput.'
    ]

    # Check some edge cases that are easy to work out by hand.
    assert True, "This prints if this assert fails 2 (also good for debugging!)"



def __run_tests():
    check(globals().get('odd_count'))

if __name__ == '__main__':
    __run_tests()

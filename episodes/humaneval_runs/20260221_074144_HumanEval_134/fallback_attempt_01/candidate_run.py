def check_if_last_char_is_a_letter(txt):
    txt = txt.rstrip()
    if not txt:
        return False
    return txt[-1].isalpha() and (len(txt) == 1 or txt[-2] == ' ')

def check(candidate):

    # Check some simple cases
    assert candidate("apple") == False
    assert candidate("apple pi e") == True
    assert candidate("eeeee") == False
    assert candidate("A") == True
    assert candidate("Pumpkin pie ") == False
    assert candidate("Pumpkin pie 1") == False
    assert candidate("") == False
    assert candidate("eeeee e ") == False
    assert candidate("apple pie") == False
    assert candidate("apple pi e ") == False

    # Check some edge cases that are easy to work out by hand.
    assert True



def __run_tests():
    check(globals().get('check_if_last_char_is_a_letter'))

if __name__ == '__main__':
    __run_tests()

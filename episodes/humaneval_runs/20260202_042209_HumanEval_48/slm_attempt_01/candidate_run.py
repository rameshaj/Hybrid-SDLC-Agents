def is_palindrome(text: str):
    return text == text[::-1]



METADATA = {}


def check(candidate):
    assert candidate('') == True
    assert candidate('aba') == True
    assert candidate('aaaaa') == True
    assert candidate('zbcd') == False
    assert candidate('xywyx') == True
    assert candidate('xywyz') == False
    assert candidate('xywzx') == False



def __run_tests():
    check(globals().get('is_palindrome'))

if __name__ == '__main__':
    __run_tests()

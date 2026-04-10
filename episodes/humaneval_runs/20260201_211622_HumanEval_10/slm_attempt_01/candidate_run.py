def make_palindrome(string: str) -> str:
    if not string:
        return ''
    
    # Find the longest palindromic suffix
    for i in range(len(string), -1, -1):
        if string[:i] == string[:i][::-1]:
            break
    
    # Append the reverse of the prefix to the end of the string
    return string + string[:i][::-1]



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('') == ''
    assert candidate('x') == 'x'
    assert candidate('xyz') == 'xyzyx'
    assert candidate('xyx') == 'xyx'
    assert candidate('jerry') == 'jerryrrej'


def __run_tests():
    check(globals().get('make_palindrome'))

if __name__ == '__main__':
    __run_tests()

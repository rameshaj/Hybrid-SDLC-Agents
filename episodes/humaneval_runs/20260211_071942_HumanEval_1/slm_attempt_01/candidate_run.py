def separate_paren_groups(paren_string: str) -> List[str]:
    groups = []
    current_group = ''
    depth = 0

    for char in paren_string.replace(' ', ''):
        if char == '(':
            depth += 1
            current_group += char
        elif char == ')':
            depth -= 1
            current_group += char
            if depth == 0:
                groups.append(current_group)
                current_group = ''

    return groups



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('(()()) ((())) () ((())()())') == [
        '(()())', '((()))', '()', '((())()())'
    ]
    assert candidate('() (()) ((())) (((())))') == [
        '()', '(())', '((()))', '(((())))'
    ]
    assert candidate('(()(())((())))') == [
        '(()(())((())))'
    ]
    assert candidate('( ) (( )) (( )( ))') == ['()', '(())', '(()())']


def __run_tests():
    check(globals().get('separate_paren_groups'))

if __name__ == '__main__':
    __run_tests()

def separate_paren_groups(paren_string: str) -> list:
    groups = []
    current_group = []
    balance = 0
    
    for char in paren_string:
        if char == '(':
            if balance == 0 and current_group:
                groups.append(''.join(current_group).replace(' ', ''))
                current_group = []
            current_group.append(char)
            balance += 1
        elif char == ')':
            current_group.append(char)
            balance -= 1
            if balance == 0:
                groups.append(''.join(current_group).replace(' ', ''))
                current_group = []
        elif char == ' ':
            continue
    
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

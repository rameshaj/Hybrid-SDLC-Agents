def parse_nested_parens(paren_string: str) -> List[int]:
    levels = []
    current_level = 0
    for char in paren_string:
        if char == '(':
            current_level += 1
            levels.append(current_level)
        elif char == ')':
            current_level -= 1
    return levels



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('(()()) ((())) () ((())()())') == [2, 3, 1, 3]
    assert candidate('() (()) ((())) (((())))') == [1, 2, 3, 4]
    assert candidate('(()(())((())))') == [4]


def __run_tests():
    check(globals().get('parse_nested_parens'))

if __name__ == '__main__':
    __run_tests()

def parse_nested_parens(paren_string: str) -> list:
    results = []
    for group in paren_string.split():
        max_depth = 0
        current_depth = 0
        for char in group:
            if char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == ')':
                current_depth -= 1
        results.append(max_depth)
    return results



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

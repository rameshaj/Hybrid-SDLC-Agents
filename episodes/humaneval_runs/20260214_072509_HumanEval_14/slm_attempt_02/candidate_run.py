def all_prefixes(string: str) -> List[str]:
    """ Return list of all prefixes from shortest to longest of the input string
    >>> all_prefixes('abc')
    ['a', 'ab', 'abc']
    """

- Import `List` from `typing`.
- Use `list` instead of `List` in the return statement.
- Fix the typo in the function name from `all_prefixes` to `all_prefixes`.



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('') == []
    assert candidate('asdfgh') == ['a', 'as', 'asd', 'asdf', 'asdfg', 'asdfgh']
    assert candidate('WWW') == ['W', 'WW', 'WWW']


def __run_tests():
    check(globals().get('all_prefixes'))

if __name__ == '__main__':
    __run_tests()

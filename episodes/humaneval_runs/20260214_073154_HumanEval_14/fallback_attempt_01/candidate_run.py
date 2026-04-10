def all_prefixes(string: str) -> list:
    return [string[:i] for i in range(1, len(string) + 1)]



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

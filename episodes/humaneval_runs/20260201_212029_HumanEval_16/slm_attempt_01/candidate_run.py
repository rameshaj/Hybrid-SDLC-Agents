def count_distinct_characters(string: str) -> int:
    return len(set(string.lower()))



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('') == 0
    assert candidate('abcde') == 5
    assert candidate('abcde' + 'cade' + 'CADE') == 5
    assert candidate('aaaaAAAAaaaa') == 1
    assert candidate('Jerry jERRY JeRRRY') == 5


def __run_tests():
    check(globals().get('count_distinct_characters'))

if __name__ == '__main__':
    __run_tests()

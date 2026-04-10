def strlen(string: str) -> int:
    return len(string)



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('') == 0
    assert candidate('x') == 1
    assert candidate('asdasnakj') == 9


def __run_tests():
    check(globals().get('strlen'))

if __name__ == '__main__':
    __run_tests()

def flip_case(string: str) -> str:
    return ''.join(c.lower() if c.isupper() else c.upper() for c in string)



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('') == ''
    assert candidate('Hello!') == 'hELLO!'
    assert candidate('These violent delights have violent ends') == 'tHESE VIOLENT DELIGHTS HAVE VIOLENT ENDS'


def __run_tests():
    check(globals().get('flip_case'))

if __name__ == '__main__':
    __run_tests()

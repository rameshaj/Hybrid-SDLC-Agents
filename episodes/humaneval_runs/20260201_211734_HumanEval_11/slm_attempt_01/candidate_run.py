def string_xor(a: str, b: str) -> str:
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('111000', '101010') == '010010'
    assert candidate('1', '1') == '0'
    assert candidate('0101', '0000') == '0101'


def __run_tests():
    check(globals().get('string_xor'))

if __name__ == '__main__':
    __run_tests()

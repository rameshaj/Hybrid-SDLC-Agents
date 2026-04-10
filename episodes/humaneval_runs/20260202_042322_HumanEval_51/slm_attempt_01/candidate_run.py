def remove_vowels(text):
    return ''.join([char for char in text if char.lower() not in 'aeiou'])



METADATA = {}


def check(candidate):
    assert candidate('') == ''
    assert candidate("abcdef\nghijklm") == 'bcdf\nghjklm'
    assert candidate('fedcba') == 'fdcb'
    assert candidate('eeeee') == ''
    assert candidate('acBAA') == 'cB'
    assert candidate('EcBOO') == 'cB'
    assert candidate('ybcd') == 'ybcd'



def __run_tests():
    check(globals().get('remove_vowels'))

if __name__ == '__main__':
    __run_tests()

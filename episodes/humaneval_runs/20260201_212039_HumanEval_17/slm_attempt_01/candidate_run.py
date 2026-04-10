def parse_music(music_string: str) -> List[int]:
    return [4 if note == 'o' else 2 if note == 'o|' else 1 for note in music_string.split()]



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('') == []
    assert candidate('o o o o') == [4, 4, 4, 4]
    assert candidate('.| .| .| .|') == [1, 1, 1, 1]
    assert candidate('o| o| .| .| o o o o') == [2, 2, 1, 1, 4, 4, 4, 4]
    assert candidate('o| .| o| .| o o| o o|') == [2, 1, 2, 1, 4, 2, 4, 2]


def __run_tests():
    check(globals().get('parse_music'))

if __name__ == '__main__':
    __run_tests()

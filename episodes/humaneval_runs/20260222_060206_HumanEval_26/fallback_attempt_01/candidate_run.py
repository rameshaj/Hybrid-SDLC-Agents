def remove_duplicates(numbers: List[int]) -> List[int]:
    seen = set()
    duplicates = set()
    result = []
    
    for number in numbers:
        if number in seen:
            duplicates.add(number)
        else:
            seen.add(number)
    
    for number in numbers:
        if number not in duplicates:
            result.append(number)
    
    return result



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate([]) == []
    assert candidate([1, 2, 3, 4]) == [1, 2, 3, 4]
    assert candidate([1, 2, 3, 2, 4, 3, 5]) == [1, 4, 5]


def __run_tests():
    check(globals().get('remove_duplicates'))

if __name__ == '__main__':
    __run_tests()

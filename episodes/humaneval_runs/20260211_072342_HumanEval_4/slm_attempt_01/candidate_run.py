def mean_absolute_deviation(numbers: List[float]) -> float:
    return sum(abs(x - sum(numbers) / len(numbers)) for x in numbers) / len(numbers)



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert abs(candidate([1.0, 2.0, 3.0]) - 2.0/3.0) < 1e-6
    assert abs(candidate([1.0, 2.0, 3.0, 4.0]) - 1.0) < 1e-6
    assert abs(candidate([1.0, 2.0, 3.0, 4.0, 5.0]) - 6.0/5.0) < 1e-6



def __run_tests():
    check(globals().get('mean_absolute_deviation'))

if __name__ == '__main__':
    __run_tests()

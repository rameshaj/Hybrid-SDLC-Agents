def add(x: int, y: int) -> int:
    return x + y



METADATA = {}


def check(candidate):
    import random

    assert candidate(0, 1) == 1
    assert candidate(1, 0) == 1
    assert candidate(2, 3) == 5
    assert candidate(5, 7) == 12
    assert candidate(7, 5) == 12

    for i in range(100):
        x, y = random.randint(0, 1000), random.randint(0, 1000)
        assert candidate(x, y) == x + y



def __run_tests():
    check(globals().get('add'))

if __name__ == '__main__':
    __run_tests()

def factorial(x):
        result = 1
        for i in range(1, x + 1):
            result *= i
        return result

    def sum_to(x):
        return x * (x + 1) // 2

    result = []
    for i in range(1, n + 1):
        if i % 2 == 0:
            result.append(factorial(i))
        else:
            result.append(sum_to(i))
    return result

def check(candidate):

    assert candidate(5) == [1, 2, 6, 24, 15]
    assert candidate(7) == [1, 2, 6, 24, 15, 720, 28]
    assert candidate(1) == [1]
    assert candidate(3) == [1, 2, 6]


def __run_tests():
    check(globals().get('f'))

if __name__ == '__main__':
    __run_tests()

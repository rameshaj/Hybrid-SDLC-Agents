def prime_fib(n: int):
    def is_prime(num):
        if num <= 1:
            return False
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                return False
        return True

    a, b = 0, 1
    count = 0
    while True:
        if is_prime(a) and count == n:
            return a
        a, b = b, a + b
        count += 1



METADATA = {}


def check(candidate):
    assert candidate(1) == 2
    assert candidate(2) == 3
    assert candidate(3) == 5
    assert candidate(4) == 13
    assert candidate(5) == 89
    assert candidate(6) == 233
    assert candidate(7) == 1597
    assert candidate(8) == 28657
    assert candidate(9) == 514229
    assert candidate(10) == 433494437



def __run_tests():
    check(globals().get('prime_fib'))

if __name__ == '__main__':
    __run_tests()

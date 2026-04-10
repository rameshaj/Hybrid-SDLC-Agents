def prime_fib(n: int):
    def is_prime(num):
        if num <= 1:
            return False
        if num <= 3:
            return True
        if num % 2 == 0 or num % 3 == 0:
            return False
        i = 5
        while i * i <= num:
            if num % i == 0 or num % (i + 2) == 0:
                return False
            i += 6
        return True

    def fibonacci():
        a, b = 0, 1
        while True:
            yield b
            a, b = b, a + b

    count = 0
    for fib in fibonacci():
        if is_prime(fib):
            count += 1
            if count == n:
                return fib



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

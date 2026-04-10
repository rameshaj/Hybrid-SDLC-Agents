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
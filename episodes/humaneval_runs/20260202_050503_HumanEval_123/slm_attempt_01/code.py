def get_odd_collatz(n):
    def collatz(n):
        while n != 1:
            if n % 2 == 0:
                n //= 2
            else:
                n = 3 * n + 1
        return [n]
    
    return sorted([num for num in collatz(n) if num % 2 != 0])
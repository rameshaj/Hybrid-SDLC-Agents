def get_odd_collatz(n):
    if n <= 0:
        return []
    
    collatz_sequence = []
    while n != 1:
        if n % 2 != 0:
            collatz_sequence.append(n)
        n = n // 2 if n % 2 == 0 else 3 * n + 1
    
    return sorted(collatz_sequence)
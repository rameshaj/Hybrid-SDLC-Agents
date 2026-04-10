def get_odd_collatz(n):
    if not isinstance(n, int) or n <= 0:
        raise ValueError("Input must be a positive integer")
    
    odd_numbers = []
    while n != 1:
        if n % 2 != 0:
            odd_numbers.append(n)
        n = (3 * n + 1) // 2
    
    return sorted(odd_numbers)
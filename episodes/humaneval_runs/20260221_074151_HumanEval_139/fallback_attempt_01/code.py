def special_factorial(n):
    def factorial(x):
        if x == 0 or x == 1:
            return 1
        result = 1
        for i in range(2, x + 1):
            result *= i
        return result

    special_fact = 1
    for i in range(1, n + 1):
        special_fact *= factorial(i)
    
    return special_fact
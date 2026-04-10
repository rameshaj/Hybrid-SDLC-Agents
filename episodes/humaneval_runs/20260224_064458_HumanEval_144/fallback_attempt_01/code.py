def simplify(x, n):
    x_num, x_den = map(int, x.split('/'))
    n_num, n_den = map(int, n.split('/'))
    
    # Multiply the fractions
    result_num = x_num * n_num
    result_den = x_den * n_den
    
    # Simplify the result
    common_divisor = gcd(result_num, result_den)
    result_num //= common_divisor
    result_den //= common_divisor
    
    # Check if the result is a whole number
    return result_den == 1
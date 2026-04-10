def simplify(x, n):
    x_num, x_den = map(int, x.split('/'))
    n_num, n_den = map(int, n.split('/'))
    
    # Simplify the fractions
    gcd_x = gcd(x_num, x_den)
    gcd_n = gcd(n_num, n_den)
    
    x_num //= gcd_x
    x_den //= gcd_x
    
    n_num //= gcd_n
    n_den //= gcd_n
    
    # Check if the product of the simplified fractions is a whole number
    return (x_num * n_num) % (x_den * n_den) == 0
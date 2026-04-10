def prod_signs(arr):
    if not arr:
        return None
    sign_product = 1
    for num in arr:
        if num == 0:
            return 0
        sign_product *= -1 if num < 0 else 1
    return sum(abs(num) * sign_product for num in arr)
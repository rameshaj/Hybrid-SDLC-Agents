def sum_product(numbers):
    total_sum = sum(numbers)
    total_product = 1
    for number in numbers:
        total_product *= number
    return (total_sum, total_product) if numbers else (0, 1)
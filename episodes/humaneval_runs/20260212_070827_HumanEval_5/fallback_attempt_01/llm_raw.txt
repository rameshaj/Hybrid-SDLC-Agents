def intersperse(numbers, delimeter):
    result = []
    for i, number in enumerate(numbers):
        result.append(number)
        if i < len(numbers) - 1:
            result.append(delimeter)
    return result
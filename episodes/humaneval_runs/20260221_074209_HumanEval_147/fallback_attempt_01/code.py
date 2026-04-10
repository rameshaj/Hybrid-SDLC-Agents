def get_max_triples(n):
    a = [i * i - i + 1 for i in range(1, n + 1)]
    count = [0, 0, 0]
    
    for num in a:
        count[num % 3] += 1
    
    result = 0
    result += count[0] * (count[0] - 1) * (count[0] - 2) // 6
    result += count[1] * (count[1] - 1) * (count[1] - 2) // 6
    result += count[2] * (count[2] - 1) * (count[2] - 2) // 6
    result += count[0] * count[1] * count[2]
    
    return result
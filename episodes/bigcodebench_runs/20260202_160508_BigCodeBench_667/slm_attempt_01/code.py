def task_func(x, n):
    return [letter for letter, _ in heapq.nlargest(n, x.items(), key=lambda item: item[1])]
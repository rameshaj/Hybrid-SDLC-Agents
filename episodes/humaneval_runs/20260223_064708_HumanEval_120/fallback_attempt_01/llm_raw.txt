def maximum(arr, k):
    return sorted(sorted(arr, reverse=True)[:k]) if k > 0 else []
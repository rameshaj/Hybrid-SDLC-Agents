def has_close_elements(numbers: List[float], threshold: float) -> bool:
    return any(abs(a - b) < threshold for a, b in combinations(numbers, 2))
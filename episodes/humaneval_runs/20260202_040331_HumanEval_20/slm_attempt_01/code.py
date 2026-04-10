def find_closest_elements(numbers: List[float]) -> Tuple[float, float]:
    numbers.sort()
    return numbers[0], numbers[-1]
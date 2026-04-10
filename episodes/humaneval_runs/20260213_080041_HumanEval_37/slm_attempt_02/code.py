def sort_even(l: list):
    even_indices = [i for i in range(len(l)) if i % 2 == 0]
    return [even_indices[i] if i % 2 == 0 else sorted(l[i]) for i in range(len(l))]
def sort_even(l: list):
    even_indices = sorted(l[::2])
    return [even_indices[i] if i % 2 == 0 else l[i] for i in range(len(l))]
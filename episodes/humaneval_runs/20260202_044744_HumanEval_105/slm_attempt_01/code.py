def by_length(arr):
    if not arr: return []
    arr = sorted([x for x in arr if 1 <= x <= 9])
    arr.reverse()
    return ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'][arr]
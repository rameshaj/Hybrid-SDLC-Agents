def pluck(arr):
    if not arr or all(node % 2 != 0 for node in arr):
        return []
    
    smallest_even = min(filter(lambda x: x % 2 == 0, arr))
    index = arr.index(smallest_even)
    
    return [smallest_even, index]
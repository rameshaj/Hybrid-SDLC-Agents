def by_length(arr):
    if not arr:
        return []
    
    # Filter and sort the array
    filtered_sorted = sorted([x for x in arr if 1 <= x <= 9])
    
    # Reverse the sorted array
    reversed_sorted = filtered_sorted[::-1]
    
    # Replace each digit with its corresponding name
    names = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    result = [names[i - 1] for i in reversed_sorted]
    
    return result
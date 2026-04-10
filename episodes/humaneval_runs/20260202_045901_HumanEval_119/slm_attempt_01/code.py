def match_parens(lst):
    if len(lst) != 2:
        return 'No'
    
    left = lst[0]
    right = lst[1]
    
    # Check if the first string can be concatenated with the second to form a good string
    if left.count('(') <= right.count(')'):
        return 'Yes'
    
    # Check if the second string can be concatenated with the first to form a good string
    if right.count('(') <= left.count(')'):
        return 'Yes'
    
    return 'No'
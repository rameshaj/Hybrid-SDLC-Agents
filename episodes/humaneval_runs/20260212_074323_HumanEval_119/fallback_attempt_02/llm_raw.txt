def match_parens(lst):
    open_count = lst[0].count('(') + lst[1].count('(')
    close_count = lst[0].count(')') + lst[1].count(')')
    
    if open_count == close_count:
        return 'Yes'
    
    if abs(lst[0].count('(') - lst[1].count(')')) <= min(lst[0].count('('), lst[1].count(')')):
        return 'Yes'
    
    return 'No'
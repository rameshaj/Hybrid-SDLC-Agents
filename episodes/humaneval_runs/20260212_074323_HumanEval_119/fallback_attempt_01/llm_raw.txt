def match_parens(lst):
    open_count = lst[0].count('(') + lst[1].count('(')
    close_count = lst[0].count(')') + lst[1].count(')')
    return 'Yes' if open_count == close_count and abs(lst[0].count('(') - lst[1].count(')')) <= 1 else 'No'
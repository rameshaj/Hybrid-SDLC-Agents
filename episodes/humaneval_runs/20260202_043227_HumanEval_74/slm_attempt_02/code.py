def total_match(lst1, lst2):
    return [s for s in lst1 if len(s) < len(lst2[0])] or lst1
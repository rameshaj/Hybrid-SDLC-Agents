def exchange(lst1, lst2):
    if all(x % 2 == 0 for x in lst1):
        return "YES"
    
    odd_in_lst1 = [x for x in lst1 if x % 2 != 0]
    even_in_lst2 = [x for x in lst2 if x % 2 == 0]
    
    if len(odd_in_lst1) <= len(even_in_lst2):
        return "YES"
    
    return "NO"
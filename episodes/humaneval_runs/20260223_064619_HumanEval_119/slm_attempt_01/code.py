def match_parens(lst):
    def is_balanced(s):
        balance = 0
        for char in s:
            if char == '(':
                balance += 1
            else:
                balance -= 1
            if balance < 0:
                return False
        return balance == 0

    for i in range(len(lst)):
        if is_balanced(lst[i] + lst[(i+1) % len(lst)]):
            return 'Yes'
    return 'No'
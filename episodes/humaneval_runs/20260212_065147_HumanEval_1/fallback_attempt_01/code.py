def separate_paren_groups(paren_string: str) -> list:
    groups = []
    current_group = []
    balance = 0
    
    for char in paren_string:
        if char == '(':
            if balance == 0 and current_group:
                groups.append(''.join(current_group).replace(' ', ''))
                current_group = []
            current_group.append(char)
            balance += 1
        elif char == ')':
            current_group.append(char)
            balance -= 1
            if balance == 0:
                groups.append(''.join(current_group).replace(' ', ''))
                current_group = []
        elif char == ' ':
            continue
    
    return groups
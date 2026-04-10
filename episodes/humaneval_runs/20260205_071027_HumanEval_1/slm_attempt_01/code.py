def separate_paren_groups(paren_string: str) -> List[str]:
    
    paren_list = list(filter(None, paren_string.split())) # remove spaces and split string into a list of groups
    result = [] 
    temp = ""
    count = 0
  
    for char in paren_list:
        if char == '(':
            count += 1
            temp += char
        elif char == ')':
            count -= 1
            temp += char
            if count == 0: # when the parentheses are balanced, add to result and reset temporary string 
                result.append(temp)
                temp = ""
    return result
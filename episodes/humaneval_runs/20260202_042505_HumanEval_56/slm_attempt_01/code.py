def correct_bracketing(brackets: str):
    stack = []
    for char in brackets:
        if char == '<':
            stack.append(char)
        elif char == '>':
            if not stack or stack.pop() != '<':
                return False
    return not stack
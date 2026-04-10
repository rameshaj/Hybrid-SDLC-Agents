def fix_spaces(text):
    result = []
    space_count = 0
    for char in text:
        if char == ' ':
            space_count += 1
        else:
            if space_count > 2:
                result.append('-')
            elif space_count > 0:
                result.append('_')
            result.append(char)
            space_count = 0
    if space_count > 2:
        result.append('-')
    elif space_count > 0:
        result.append('_')
    return ''.join(result)
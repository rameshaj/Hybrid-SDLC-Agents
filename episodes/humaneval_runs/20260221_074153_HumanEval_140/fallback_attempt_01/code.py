def fix_spaces(text):
    import re
    return re.sub(r' {2,}', '-', text.replace(' ', '_'))
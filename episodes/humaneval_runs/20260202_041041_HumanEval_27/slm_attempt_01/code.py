def flip_case(string: str) -> str:
    return ''.join(c.lower() if c.isupper() else c.upper() for c in string)
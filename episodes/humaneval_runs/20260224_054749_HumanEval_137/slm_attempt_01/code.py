def compare_one(a, b):
    if isinstance(a, str) and isinstance(b, str):
        a = float(a.replace(',', '.'))
        b = float(b.replace(',', '.'))
    elif not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return None
    
    return max(a, b)
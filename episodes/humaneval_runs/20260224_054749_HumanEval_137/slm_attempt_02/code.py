def compare_one(a, b):
    if isinstance(a, str) and isinstance(b, str):
        a = float(a.replace(',', '.'))
        b = float(b.replace(',', '.'))
    
    if isinstance(a, float) and isinstance(b, float):
        return max(a, b)
    
    if isinstance(a, int) and isinstance(b, int):
        return max(a, b)
    
    return None
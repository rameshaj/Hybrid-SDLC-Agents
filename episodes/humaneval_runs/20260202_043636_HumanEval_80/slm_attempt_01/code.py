def is_happy(s):
    return len(s) >= 3 and all(len(set(s[i:i+3])) == 3 for i in range(len(s)-2))
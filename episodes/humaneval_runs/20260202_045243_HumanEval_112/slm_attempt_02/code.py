def reverse_delete(s, c):
    return ''.join([char for char in s if char not in c]), s == s[::-1]
def select_words(s, n):
    if not s:
        return []
    
    words = s.split()
    selected_words = [word for word in words if len(word) == n and sum(c.isalpha() for c in word) - word.count('a') - word.count('e') - word.count('i') - word.count('o') - word.count('u') == n]
    
    return selected_words
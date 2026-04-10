def histogram(test):
    if not test:
        return {}
    
    letters = test.split()
    letter_counts = {}
    
    for letter in letters:
        if letter in letter_counts:
            letter_counts[letter] += 1
        else:
            letter_counts[letter] = 1
    
    max_count = max(letter_counts.values())
    result = {letter: count for letter, count in letter_counts.items() if count == max_count}
    
    return result
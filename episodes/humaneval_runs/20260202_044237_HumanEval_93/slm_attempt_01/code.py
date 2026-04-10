def encode(message):
    vowels = 'aeiouAEIOU'
    result = ''
    for char in message:
        if char.isalpha():
            if char in vowels:
                next_vowel = vowels[(vowels.index(char) + 2) % len(vowels)]
                result += next_vowel
            else:
                result += char.swapcase()
        else:
            result += char
    return result
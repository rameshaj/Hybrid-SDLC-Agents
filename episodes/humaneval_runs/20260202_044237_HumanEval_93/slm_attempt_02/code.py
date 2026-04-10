def encode(message):
    vowels = 'aeiouAEIOU'
    for i, char in enumerate(message):
        if char in vowels:
            index = (vowels.index(char) + 2) % len(vowels)
            message = message[:i] + vowels[index] + message[i+1:]
    return message.swapcase()
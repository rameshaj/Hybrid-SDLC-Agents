def encrypt(s):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    encrypted = ""
    for char in s:
        if char.isalpha():
            index = alphabet.index(char.lower()) + (2 * 2)
            encrypted += alphabet[index % 26]
        else:
            encrypted += char
    return encrypted
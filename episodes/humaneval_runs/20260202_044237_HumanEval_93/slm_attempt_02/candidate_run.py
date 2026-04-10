def encode(message):
    vowels = 'aeiouAEIOU'
    for i, char in enumerate(message):
        if char in vowels:
            index = (vowels.index(char) + 2) % len(vowels)
            message = message[:i] + vowels[index] + message[i+1:]
    return message.swapcase()

def check(candidate):

    # Check some simple cases
    assert candidate('TEST') == 'tgst', "This prints if this assert fails 1 (good for debugging!)"
    assert candidate('Mudasir') == 'mWDCSKR', "This prints if this assert fails 2 (good for debugging!)"
    assert candidate('YES') == 'ygs', "This prints if this assert fails 3 (good for debugging!)"
    
    # Check some edge cases that are easy to work out by hand.
    assert candidate('This is a message') == 'tHKS KS C MGSSCGG', "This prints if this assert fails 2 (also good for debugging!)"
    assert candidate("I DoNt KnOw WhAt tO WrItE") == 'k dQnT kNqW wHcT Tq wRkTg', "This prints if this assert fails 2 (also good for debugging!)"



def __run_tests():
    check(globals().get('encode'))

if __name__ == '__main__':
    __run_tests()

def fix_spaces(text):
    result = []
    space_count = 0
    for char in text:
        if char == ' ':
            space_count += 1
        else:
            if space_count > 2:
                result.append('-')
            elif space_count > 0:
                result.append('_')
            result.append(char)
            space_count = 0
    if space_count > 2:
        result.append('-')
    elif space_count > 0:
        result.append('_')
    return ''.join(result)

def check(candidate):

    # Check some simple cases
    assert candidate("Example") == "Example", "This prints if this assert fails 1 (good for debugging!)"
    assert candidate("Mudasir Hanif ") == "Mudasir_Hanif_", "This prints if this assert fails 2 (good for debugging!)"
    assert candidate("Yellow Yellow  Dirty  Fellow") == "Yellow_Yellow__Dirty__Fellow", "This prints if this assert fails 3 (good for debugging!)"
    
    # Check some edge cases that are easy to work out by hand.
    assert candidate("Exa   mple") == "Exa-mple", "This prints if this assert fails 4 (good for debugging!)"
    assert candidate("   Exa 1 2 2 mple") == "-Exa_1_2_2_mple", "This prints if this assert fails 4 (good for debugging!)"



def __run_tests():
    check(globals().get('fix_spaces'))

if __name__ == '__main__':
    __run_tests()

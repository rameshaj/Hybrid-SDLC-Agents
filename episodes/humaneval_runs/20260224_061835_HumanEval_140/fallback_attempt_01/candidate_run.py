def fix_spaces(text):
    result = []
    i = 0
    while i < len(text):
        if text[i] == ' ':
            space_count = 0
            while i < len(text) and text[i] == ' ':
                space_count += 1
                i += 1
            if space_count > 2:
                result.append('-')
            else:
                result.append('_' * space_count)
        else:
            result.append(text[i])
            i += 1
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

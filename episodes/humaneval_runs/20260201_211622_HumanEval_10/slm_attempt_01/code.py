def make_palindrome(string: str) -> str:
    if not string:
        return ''
    
    # Find the longest palindromic suffix
    for i in range(len(string), -1, -1):
        if string[:i] == string[:i][::-1]:
            break
    
    # Append the reverse of the prefix to the end of the string
    return string + string[:i][::-1]
def make_palindrome(string: str) -> str:
    """ Find the shortest palindrome that begins with a supplied string.
    Algorithm idea is simple:
    - Find the longest postfix of supplied string that is a palindrome.
    - Append to the end of the string reverse of a string prefix that comes before the palindromic suffix.
    >>> make_palindrome('')
    ''
    >>> make_palindrome('cat')
    'catac'
    >>> make_palindrome('cata')
    'catac'
    """
    if not string:
        return string

    # Find the longest palindromic prefix
    i = 0
    while i < len(string) and string[i] == string[-(i + 1)]:
        i += 1

    # Append the reverse of the non-palindromic suffix to the end
    return string + string[:-(i + 1)][::-1]
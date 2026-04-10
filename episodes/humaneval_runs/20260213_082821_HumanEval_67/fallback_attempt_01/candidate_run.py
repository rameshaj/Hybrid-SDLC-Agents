def fruit_distribution(s, n):
    words = s.split()
    apples = int(words[0])
    oranges = int(words[3])
    return n - apples - oranges

def check(candidate):

    # Check some simple cases
    assert candidate("5 apples and 6 oranges",19) == 8
    assert candidate("5 apples and 6 oranges",21) == 10
    assert candidate("0 apples and 1 oranges",3) == 2
    assert candidate("1 apples and 0 oranges",3) == 2
    assert candidate("2 apples and 3 oranges",100) == 95
    assert candidate("2 apples and 3 oranges",5) == 0
    assert candidate("1 apples and 100 oranges",120) == 19


def __run_tests():
    check(globals().get('fruit_distribution'))

if __name__ == '__main__':
    __run_tests()

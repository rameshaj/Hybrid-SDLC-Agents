def correct_bracketing(brackets: str):
    stack = []
    for char in brackets:
        if char == '<':
            stack.append(char)
        elif char == '>':
            if not stack or stack.pop() != '<':
                return False
    return not stack



METADATA = {}


def check(candidate):
    assert candidate("<>")
    assert candidate("<<><>>")
    assert candidate("<><><<><>><>")
    assert candidate("<><><<<><><>><>><<><><<>>>")
    assert not candidate("<<<><>>>>")
    assert not candidate("><<>")
    assert not candidate("<")
    assert not candidate("<<<<")
    assert not candidate(">")
    assert not candidate("<<>")
    assert not candidate("<><><<><>><>><<>")
    assert not candidate("<><><<><>><>>><>")



def __run_tests():
    check(globals().get('correct_bracketing'))

if __name__ == '__main__':
    __run_tests()

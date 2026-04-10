def do_algebra(operator, operand):
    expression = str(operand[0])
    for i, op in enumerate(operator):
        expression += f" {op} {operand[i + 1]}"
    return eval(expression)

def check(candidate):

    # Check some simple cases
    assert candidate(['**', '*', '+'], [2, 3, 4, 5]) == 37
    assert candidate(['+', '*', '-'], [2, 3, 4, 5]) == 9
    assert candidate(['//', '*'], [7, 3, 4]) == 8, "This prints if this assert fails 1 (good for debugging!)"

    # Check some edge cases that are easy to work out by hand.
    assert True, "This prints if this assert fails 2 (also good for debugging!)"



def __run_tests():
    check(globals().get('do_algebra'))

if __name__ == '__main__':
    __run_tests()

def match_parens(lst):
    open_count = lst[0].count('(') + lst[1].count('(')
    close_count = lst[0].count(')') + lst[1].count(')')
    return 'Yes' if open_count == close_count and abs(lst[0].count('(') - lst[1].count(')')) <= 1 else 'No'

def check(candidate):

    # Check some simple cases
    assert candidate(['()(', ')']) == 'Yes'
    assert candidate([')', ')']) == 'No'
    assert candidate(['(()(())', '())())']) == 'No'
    assert candidate([')())', '(()()(']) == 'Yes'
    assert candidate(['(())))', '(()())((']) == 'Yes'
    assert candidate(['()', '())']) == 'No'
    assert candidate(['(()(', '()))()']) == 'Yes'
    assert candidate(['((((', '((())']) == 'No'
    assert candidate([')(()', '(()(']) == 'No'
    assert candidate([')(', ')(']) == 'No'
    

    # Check some edge cases that are easy to work out by hand.
    assert candidate(['(', ')']) == 'Yes'
    assert candidate([')', '(']) == 'Yes' 



def __run_tests():
    check(globals().get('match_parens'))

if __name__ == '__main__':
    __run_tests()

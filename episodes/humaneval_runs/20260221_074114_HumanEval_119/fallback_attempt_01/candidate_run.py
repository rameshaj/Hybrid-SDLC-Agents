def match_parens(lst):
    open_count_1 = lst[0].count('(')
    close_count_1 = lst[0].count(')')
    open_count_2 = lst[1].count('(')
    close_count_2 = lst[1].count(')')

    if open_count_1 + open_count_2 == close_count_1 + close_count_2:
        return 'Yes'
    return 'No'

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

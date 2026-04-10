def match_parens(lst):
    if len(lst) != 2:
        return 'No'
    
    left = lst[0]
    right = lst[1]
    
    # Check if the first string can be concatenated with the second to form a good string
    if left.count('(') <= right.count(')'):
        return 'Yes'
    
    # Check if the second string can be concatenated with the first to form a good string
    if right.count('(') <= left.count(')'):
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

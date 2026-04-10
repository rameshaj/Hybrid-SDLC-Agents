def odd_count(lst):
    return ["the number of odd elements {}n the str{}ng {} of the {}nput.".format(len([x for x in lst[i] if int(x) % 2 != 0]), i+1, lst[i], i+1) for i in range(len(lst))]
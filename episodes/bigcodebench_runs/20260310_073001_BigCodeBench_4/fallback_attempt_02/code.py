def task_func(d):
    return dict(Counter(itertools.chain.from_iterable(d.values())))
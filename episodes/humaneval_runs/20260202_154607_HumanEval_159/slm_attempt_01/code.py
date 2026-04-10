def eat(number, need, remaining):
    return [number + min(need, remaining), remaining - min(need, remaining)]
def task_func(x=1):
    hands = [random.sample(CARDS, 5) for _ in range(x)]
    drawn_cards = [card for hand in hands for card in hand]
    return hands, Counter(drawn_cards)
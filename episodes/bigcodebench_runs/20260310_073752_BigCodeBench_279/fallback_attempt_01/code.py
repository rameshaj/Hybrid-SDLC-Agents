def task_func(x=1):
    hands = []
    drawn_cards = []
    
    for _ in range(x):
        hand = random.sample(CARDS, 5)
        hands.append(hand)
        drawn_cards.extend(hand)
    
    card_counter = Counter(drawn_cards)
    
    return hands, card_counter
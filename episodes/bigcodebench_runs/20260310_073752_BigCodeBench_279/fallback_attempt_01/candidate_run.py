def task_func(x=1):
    hands = []
    drawn_cards = []
    
    for _ in range(x):
        hand = random.sample(CARDS, 5)
        hands.append(hand)
        drawn_cards.extend(hand)
    
    card_counter = Counter(drawn_cards)
    
    return hands, card_counter

import unittest
import random
class TestCases(unittest.TestCase):
    def test_hand_size(self):
        """ Test if the hand contains exactly 5 cards. """
        random.seed(0)
        hand, _ = task_func()
        self.assertEqual(len(hand[0]), 5)
    
    
    def test_drawn_size(self):
        random.seed(0)
        hand, _ = task_func(2)
        self.assertEqual(len(hand[0]), 5)
        self.assertEqual(len(hand), 2)
    
    def test_counter(self):
        random.seed(0)
        hand, counter = task_func(1)
        self.assertEqual(len(hand[0]), 5)
        self.assertLessEqual(counter[hand[0][0]], 5)
        self.assertGreaterEqual(counter[hand[0][0]], 1)
    def test_card_uniqueness(self):
        """ Test if all cards in the hand are unique. """
        random.seed(0)
        hand, _ = task_func()
        self.assertEqual(len(hand[0]), len(set(hand[0])))
    def test_valid_cards(self):
        """ Test if all cards drawn are valid card values. """
        random.seed(0)
        hand, _ = task_func()
        for card in hand[0]:
            self.assertIn(card, ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'])
    def test_randomness(self):
        """ Test if multiple executions return different hands. """
        random.seed(0)
        hands = [task_func()[0][0] for _ in range(10)]
        self.assertTrue(len(set(tuple(hand) for hand in hands[0])) > 1)
    def test_card_distribution(self):
        """ Test if all possible cards appear over multiple executions. """
        random.seed(0)
        all_cards = set()
        for _ in range(1000):
            all_cards.update(task_func()[0][0])
        self.assertEqual(all_cards, set(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']))

if __name__ == '__main__':
    import unittest
    unittest.main()

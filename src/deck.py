import random
from card import Card

class Deck:
    def __init__(self):
        self.cards = []
        self.generate_dobble_deck()

    def generate_dobble_deck(self):
        q = 7
        cards = []
        for i in range(q + 1):
            card_symbols = [i]
            for j in range(q):
                symbol = q + 1 + (j + i) % q
                card_symbols.append(symbol)
            cards.append(Card(len(cards), card_symbols))
        for i in range(q):
            for j in range(q):
                card_symbols = []
                for k in range(q):
                    symbol = q + 1 + (j + i * k) % q
                    card_symbols.append(symbol)
                card_symbols.append(i)
                cards.append(Card(len(cards), card_symbols))
        self.cards = cards[:57]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        if self.cards:
            return self.cards.pop()
        return None

    def remaining(self):
        return len(self.cards)
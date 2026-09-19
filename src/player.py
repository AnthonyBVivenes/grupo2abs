class Player:
    def __init__(self, name, is_human=True):
        self.name = name
        self.is_human = is_human
        self.hand = []
        self.score = 0
        self.correct = 0
        self.incorrect = 0

    def add_card(self, card):
        self.hand.append(card)

    def remove_card(self, card):
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False

    def find_common_symbol(self, card1, card2):
        set1 = set(card1.symbols)
        set2 = set(card2.symbols)
        common = set1.intersection(set2)
        if common:
            return common.pop()
        return None

    def play_turn(self, game):
        if not self.is_human:
            if game.center_card and self.hand:
                own_card = self.hand[0]
                common = self.find_common_symbol(own_card, game.center_card)
                if common is not None:
                    claimed = game.deck.draw_card()
                    if claimed:
                        self.add_card(claimed)
                        self.score += 1
                        return True
        return False
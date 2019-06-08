from collections import defaultdict
from random import shuffle

class BasicCard:
    """An abstract card class to be modified by individual games."""
    def __init__(self, name: str, image: str):
        self.name = name
        self.image = image

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name})'


class Deck:
    """Handles deck management including distribution and shuffling."""
    def __init__(self):
        self.cards = []
        self.counts = defaultdict(int)

    def insert(self, card, count=1):
        """Inserts a card into the deck, or multiple cards."""
        for _ in range(count):
            self.cards.append(card)
            self.counts[card] += 1

    def remove(self, card, count=1):
        """Removes a card from the deck, or multiple cards."""
        for _ in range(count):
            self.cards.remove(card)
            self.counts[card] -= 1

    def pop(self, index=-1):
        """Returns the top card, or at the position specified."""
        return self.cards.pop(index)

    def top(self, count=1):
        """Returns the top (count) cards of the deck."""
        return [self.pop(-1) for _ in range(count)]

    def bottom(self, count=1):
        """Returns the bottom (count) cards of the deck."""
        return [self.pop(0) for _ in range(count)]

    def shuffle(self):
        """Shuffles the deck."""
        shuffle(self.cards)

    def count_of(self, **criteria):
        """Returns the number of cards in the deck matching specified criteria."""
        count = 0
        for card in self.cards:
            if all(getattr(card, k) == v for k, v in criteria.items()):
                count += 1
        return count

    def __getitem__(self, key):
        return self.cards.__getitem__(key)

    def __setitem__(self, key, value):
        self.cards.__setitem__(key, value)

    def __delitem__(self, key):
        self.cards.__delitem__(key)

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f'Deck(cards=[' + ', '.join(f'{card} ({count})' for card, count in self.counts.items()) + '])'
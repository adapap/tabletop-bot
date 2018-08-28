class Card:
    def __init__(self, *, img_src: str):
        self.img_src = img_src

class VotingCard(Card):
    def __init__(self, *, img_src: str):
        super().__init__(img_src)

class PolicyCard(Card):
    def __init__(self, *, img_src: str, card_type: str):
        super().__init__(img_src)
        self.card_type = card_type

class IdentityCard(Card):
    def __init__(self, *, img_src: str):
        super().__init__(img_src)
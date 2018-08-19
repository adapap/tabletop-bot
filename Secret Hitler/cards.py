class Card:
    def __init__(self, *, img_src: str):
        pass

class VotingCard(Card):
    def __init__(self, *, img_src: str):
        super().__init__(img_src)

class PolicyCard(Card):
    def __init__(self, *, img_src: str):
        super().__init__(img_src)

class IdentityCard(Card):
    def __init__(self, *, img_src: str):
        super().__init__(img_src)
from Card import BasicCard

class PolicyCard(BasicCard):
    def __init__(self, *, card_type: str, image: str):
        self.card_type = card_type
        self.image = image

    @property
    def name(self):
        return self.card_type.title()
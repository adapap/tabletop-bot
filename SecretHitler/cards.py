from copy import deepcopy
from PIL import Image

class Card:
    def __init__(self, *, img_src: str):
        self.img_src = img_src


class VotingCard(Card):
    def __init__(self, *, img_src: str):
        super().__init__(img_src=img_src)


class PolicyCard(Card):
    def __init__(self, *, img_src: str, card_type: str):
        super().__init__(img_src=img_src)
        self.card_type = card_type


class IdentityCard(Card):
    def __init__(self, *, img_src: str):
        super().__init__(img_src=img_src)


class Tracker:
    """Data class for election tracker."""
    def __init__(self, *, count: int, x: int, y: int, offset: int, icon: Image):
        self.count = count
        self.x = x
        self.y = y
        self.offset = offset
        self.icon = icon

class Policy:
    """Data class for policy cards."""
    def __init__(self, *, x: int, y: int, offset: int, _type: str):
        self.x = x
        self.y = y
        self.offset = offset
        self.type = _type
        self.img = Image.open(f'SecretHitler/assets/{_type}_policy.png')


class Board:
    """Board object, used to implement the Liberal and Fascist boards and manage how policies are added to them."""
    def __init__(self, *, policy: Policy):
        self.policy = policy
        self.board = Image.open(f'SecretHitler/assets/{self.policy.type}_board.png')

    def add_policy(self):
        self.board.alpha_composite(self.policy.img, (self.policy.x, self.policy.y))
        self.policy.x += self.policy.offset

    def show_board(self):
        self.board.show()


class LiberalBoard(Board):
    """Liberal board object that has the unique quality of the election tracker."""
    def __init__(self):
        super().__init__(policy=Policy(x=445, y=195, offset=492, _type='liberal'))
        self.election_tracker = Tracker(count=0, x=1100, y=915, offset=330, icon=Image.open('SecretHitler/assets/election_tracker.png'))

    def show_board(self):
        tracker = self.election_tracker
        display_board = deepcopy(self.board)
        display_board.alpha_composite(tracker.icon, (tracker.x + (tracker.count * tracker.offset), tracker.y))
        display_board.show()

    def election_fail(self):
        self.election_tracker.count += 1
        if self.election_tracker.count > 3:
            self.election_tracker.count = 0


class FascistBoard(Board):
    """Fascist board object."""
    def __init__(self):
        super().__init__(policy=Policy(x=220, y=200, offset=492, _type='fascist'))


# l = LiberalBoard()
# for i in range(0, 5):
#   l.add_policy()
# l.show_board()

# f = FascistBoard()
# for i in range(0, 6):
#   f.add_policy()
# f.show_board()
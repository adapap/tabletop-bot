from PIL import Image
from copy import deepcopy

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


class Board:
	"""Board object, used to implement the Liberal and Fascist boards and manage how policies are added to them."""
	def __init__(self, *, img_src: str, policy_img_src: str, policy_pos_x: int, policy_pos_y: int, policy_pos_offset: int):
		self.policy_pos_x = policy_pos_x
		self.policy_pos_y = policy_pos_y
		self.policy_pos_offset = policy_pos_offset
		self.board = Image.open(img_src)
		self.policy = Image.open(policy_img_src)

	def add_policy(self):
		self.board.alpha_composite(self.policy, (self.policy_pos_x, self.policy_pos_y))
		self.policy_pos_x += self.policy_pos_offset

	def show_board(self):
		self.board.show()


class LiberalBoard(Board):
	"""Liberal board object that has the unique quality of the election tracker."""
	def __init__(self):
		super().__init__(img_src="assets/liberal_board.png", policy_img_src="assets/liberal_policy.png", policy_pos_x=445, policy_pos_y=195, policy_pos_offset=492)
		self.election_tracker = 0
		self.election_tracker_x = 1100
		self.election_tracker_y = 915
		self.election_tracker_offset = 330
		self.election_tracker_icon = Image.open("assets/election_tracker.png")

	def show_board(self):
		display_board = deepcopy(self.board)
		display_board.alpha_composite(self.election_tracker_icon, (self.election_tracker_x + (self.election_tracker*self.election_tracker_offset), self.election_tracker_y))
		display_board.show()

	def election_fail(self):
		self.election_tracker += 1
		if self.election_tracker > 3:
			self.election_tracker = 0


class FascistBoard(Board):
	"""Fascist board object."""
	def __init__(self):
		super().__init__(img_src="assets/fascist_board.png", policy_img_src="assets/fascist_policy.png", policy_pos_x=220, policy_pos_y=200, policy_pos_offset=488)		


# l = LiberalBoard()
# for i in range(0, 5):
# 	l.add_policy()
# l.show_board()

# for i in range(0, 6):
# 	l.election_fail()
# 	l.show_board()


# f = FascistBoard(img_src="assets/fascist_board.png", policy_img_src="assets/fascist_policy.png", policy_pos_x=220, policy_pos_y=200, policy_pos_offset=488)
# for i in range(0, 6):
# 	f.add_policy()
# f.show_board()
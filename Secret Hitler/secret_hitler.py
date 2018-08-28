from cards import *
from game import Game
from utils import EmbedColor

from itertools import cycle
from random import shuffle, choice, sample
# import packages from parent dir

# Temporary modules
from string import ascii_uppercase as alphabet


class SecretHitler(Game):
	"""
	Secret Hitler is a card game...
	"""
	def __init__(self, *, name: str):
		super().__init__(name)

		# Adding test players, should replace with a proper player join mechanic
		self.players = []
		for x in alphabet[:5]:
			self.add_player(x)

		# There are 6 fascist policies and 11 liberal policies in a deck
		self.policy_deck = []
		self.policy_deck.extend([PolicyCard(card_type="fascist", img_src="")] * 11)
		self.policy_deck.extend([PolicyCard(card_type="liberal", img_src="")] * 6)
		shuffle(self.policy_deck)
		self.policy_index = 0

		# Keeps track of enacted policies
		self.board = {
			'fascist': 0,
			'liberal': 0
		}

		# Create an iterator that cycles every game loop (when action is valid)
		# For example, "election" can be a stage
		self.stage = None
		self.prev_president = None
		self.prev_chancellor = None

	"""
	Property which gives number of policy cards in the deck
	"""
	@property
	def policy_count(self):
		return len(self.policy_deck)

	"""
	Handles nominating a chancellor. Is a dummy function that just chooses a random player right now
	"""
	def choose_chancellor(self):
		return random.choice(self.players)

	"""
	Handles getting voting results. Is a dummy function that just returns true/false right now
	"""
	def get_voting_results(self):
		return random.choice({True, False})

	"""
	Handles getting the President's chosen policies. Is a dummy function that just chooses two random policies now
	"""
	def pick_chosen_policies(self, policies):
		return random.sample(policies, 2)

	"""
	Handles getting the Chancellor's chosen policy. Is a dummy function that just chooses a random policy now
	"""
	def get_enacted_policy(self, chosen_policies):
		return random.choice(chosen_policies)

	"""
	Handles the turn-by-turn logic of the game
	"""
	def loop(self):
		president = None
		chancellor = None
		while True:
			president = self.next_player()
			self.send_message(f'{president.name} is the President now! They must nominate a Chancellor.')

			# Rewrite this into proper chancellor choosing function
			nominee = self.choose_chancellor()
			if nominee == self.prev_president or nominee == self.prev_chancellor:
				message = "You may not nominate the previous President, previous Chancellor, or yourself!"
				self.send_message(message, color=EmbedColor.ERROR)
				continue

			message = f'{nominee.name} has been nominated to be the Chancellor!'
			self.send_message(message)

			voting_results = self.get_voting_results()

			if voting_results:
				chancellor = nominee
				message = 'The Chancellor was voted in!'
				self.send_message(message, color=EmbedColor.SUCCESS)

				policies = [self.policy_deck[:self.policy_index + 3]]
				self.policy_index += 3

				message = '<' + ', '.join(policy.card_type for policy in policies) + '> Pick 2 policies to send to the Chancellor.'
				self.send_message(message, channel=president.dm_channel)

				candidate_policies = self.pick_chosen_policies(policies)
				message = '<' + ', '.join(policy.card_type for policy in candidate_policies) + '> Choose a policy to enact.'
				self.send_message(message, channel=chancellor.dm_channel)

				enacted_policy = choice(candidate_policies)
				# enacted_policy = self.get_enacted_policy(to_enact)

				# if enacted_policy.card_type == 'Liberal':
				# 	self.num_liberal_policies += 1
				# 	message = 'A liberal policy was passed!'
				# 	self.send_message(message)
				# else:
				# 	self.num_fascist_policies += 1
				# 	message = 'A fascist policy was passed!'
				# 	self.send_message(message)
				self.board[enacted_policy.card_type] += 1
				self.send_message(f'A {enacted_policy.card_type} policy was passed!')

			else:
				self.send_message('The Chancellor was voted down!', color=EmbedColor.WARN)

			if self.board['liberal'] == 5:
				self.send_message('Five liberal policies have been passed, and the Liberals win!')
				return

			if self.board['fascist'] == 6:
				self.send_message('Six liberal policies have been passed, and the Fascists win!')
				return

			# Redundant message, show image of board progress
			message = self.board['liberal'] + " liberal policies and " + self.board['fascist'] + " fascist policies have been passed."
			self.send_message(message)

			if self.policy_count - self.policy_index < 3:
				shuffle(self.policy_deck)
				self.policy_index = 0
				self.send_message('As the deck had less than three policies remaining, the deck has been reshuffled.')

			self.prev_chancellor = chancellor
			self.prev_president = president
			# Replaced with next_player
			# president_index += 1
			# if president_index >= len(self.players):
			# 	president_index %= len(self.players)


	"""
	Randomly assigns identities to players (Hitler, Liberal, Fascist, etc.)
	"""
	def assign_identities(self):
		identities = ['Hitler']
		# Add appropriate fascists depending on player count
		identities.extend(['Fascist'] * ((self.player_count - 3) // 2))
		# Remaining identities are filled with liberals
		identities.extend(['Liberal'] * ((self.player_count - len(identities))))
		shuffle(identities)
		
		# Indicate what identity a player has and inform related parties
		fascists = []
		hitler = None
		for player, identity in zip(self.players, identities):
			player.identity = identity
			if identity == 'Hitler':
				hitler = player
			elif identity == 'Fascist':
				fascists.append(player)
			self.send_message(f'You are a {identity}.', channel=player.dm_channel)
		for fascist in fascists:
			team = [f.name for f in fascists if f.name != fascist.name]
			if len(team):
				team = 'The other fascists are:\n' + '\n'.join(team)
			else:
				team = 'You are the only fascist'
			message = f'{team}\n{hitler.name} is Hitler'
			self.send_message(message, channel=fascist.dm_channel)
		if len(fascists) == 1:
			message = f'{fascists[0].name} is a fascist'
			self.send_message(message, channel=hitler.dm_channel)


	"""
	Checks if the game can start and assigns roles to players
	"""
	def start_game(self):
		if not 5 <= self.player_count <= 10:
			self.send_message("You must have between 5-10 players to start the game.", EmbedColor.ERROR)
			return
		self.assign_identities()

		# Creates an iterator which cycles through the next player
		self.player_cycle = cycle(self.players)
		self.next_player = lambda: next(self.player_cycle)

		# Starts the game loop
		self.loop()


if __name__ == "__main__":
	game = SecretHitler(name='Secret Hitler')
	# while game.player_count < 3:
	# 	name = input('Player name: ')
	# 	game.add_player(name)
	game.start_game()
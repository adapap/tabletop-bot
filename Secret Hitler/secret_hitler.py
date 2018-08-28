from game import Game
from random import shuffle, choice, sample
from utils import EmbedColor
from cards import *
# import packages from parent dir

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
		self.policy_deck.extend([PolicyCard(type="Fascist", img_src="")] * 11)
		self.policy_deck.extend([PolicyCard(type="Liberal", img_src="")] * 6)
		shuffle(self.policy_deck)
		self.policy_deck_pos = 0

		# Number of each kind of policy (may later be moved to be a property of their respective board)
		self.num_liberal_policies = 0
		self.num_fascist_policies = 0


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
	def game_loop(self):
		president_index = 0
		president = None
		chancellor = None
		prev_president = None
		prev_chancellor = None
		while True:
			president = self.players[president_index]
			message = president.name + " is the President now! They must nominate a Chancellor."
			self.send_message(message)

			nominee = self.choose_chancellor()
			if nominee == prev_president or nominee == prev_chancellor:
				message = "You may not nominate the previous President, previous Chancellor, or yourself!"
				self.send_message(message, color = EmbedColor.ERROR.value)
				continue

			message = nominee.name + " has been nominated to be the Chancellor!"
			self.send_message(message)

			voting_results = self.get_voting_results()

			if voting_results:
				chancellor = nominee
				message = "The Chancellor was voted in!"
				self.send_message(message, color = EmbedColor.SUCCESS.value)

				policies = {self.policy_deck[self.policy_deck_pos], self.policy_deck[self.policy_deck_pos + 1], self.policy_deck[self.policy_deck_pos + 2]}
				self.policy_deck_pos += 3

				message = policies[0].type + ", " + policies[1].type + ", " + policies[2].type + ": Pick 2 policies to send to the Chancellor."
				self.send_message(message, channel = president.dm_channel)

				chosen_policies = self.pick_chosen_policies(policies)
				message = chosen_policies[0].type + ", " + chosen_policies[1].type + ": Pick 1 policy to enact."
				self.send_message(message, channel = chancellor.dm_channel)

				enacted_policy = self.get_enacted_policy(chosen_policies)

				if enacted_policy.type == "Liberal":
					self.num_liberal_policies += 1
					message = "A liberal policy was passed!"
					self.send_message(message)
				else:
					self.num_fascist_policies += 1
					message = "A fascist policy was passed!"
					self.send_message(message)
			else:
				message = "The Chancellor was voted down!"
				self.send_message(message, color = EmbedColor.WARN.value)

			if(self.num_liberal_policies >= 5):
				message = "Five liberal policies have been passed, and the Liberals win!"
				self.send_message(message)
				return

			if(self.num_fascist_policies >= 6):
				message = "Six liberal policies have been passed, and the Fascists win!"
				self.send_message(message)
				return

			message = self.num_liberal_policies + " liberal policies and " + self.num_fascist_policies + " fascist policies have been passed."
			self.send_message(message)

			if len(self.policy_deck) - self.policy_deck_pos < 3:
				shuffle(self.policy_deck)
				self.policy_deck_pos = 0
				message = "As the deck had less than three policies remaining, the deck has been reshuffled."
				self.send_message(message)

			prev_chancellor = chancellor
			prev_president = president
			president_index += 1
			if president_index >= len(self.players):
				president_index %= len(self.players)


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
			self.send_message("You must have between 5-10 players to start the game.", EmbedColor.ERROR.value)
			return
		self.assign_identities()
		self.game_loop()


if __name__ == "__main__":
	game = SecretHitler(name='Secret Hitler')
	# while game.player_count < 3:
	# 	name = input('Player name: ')
	# 	game.add_player(name)
	game.start_game()
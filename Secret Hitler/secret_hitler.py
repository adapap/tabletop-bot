from game import Game
from random import shuffle
from utils import EmbedColor
# import packages from parent dir

from string import ascii_uppercase as alphabet


class SecretHitler(Game):
	"""
	Secret Hitler is a card game...
	"""
	def __init__(self, *, name: str):
		super().__init__(name)

		self.players = []
		for x in alphabet[:5]:
			self.add_player(x)

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


if __name__ == "__main__":
	game = SecretHitler(name='Secret Hitler')
	# while game.player_count < 3:
	# 	name = input('Player name: ')
	# 	game.add_player(name)
	game.start_game()
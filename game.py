class Player:
	def __init__(self, name):
		self.name = name
		self.vote = True
		self.identity = "Unassigned"
		
	def set_identity(self, identity):
		self.identity = identity

class SecretHitlerGame:
	def __init__(self):
		self.players = []
		#self.look_for_players()

	def look_for_players(self):
		name = ""
		while name != "$ready":
			name = input("Enter a name\n")
			if name != "$ready":
				self.players.append(name)
			if name == "$ready" and len(self.players) < 5:
				print("You need at least 5 players to start the game.")
				name = ""
			if len(self.players) == 10: 
				print("Game full! Starting now.")
				break
	def assign_roles(self):
		print("")





def main():
	game = SecretHitlerGame()
	game.look_for_players()

if __name__ == "__main__":
	main()
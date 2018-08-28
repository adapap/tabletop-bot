class Game:
    def __init__(self, name: str):
        self.name = name
        self.players = []
        self.channel = None

    """
    Returns the number of players in the game
    """
    @property
    def player_count(self):
        return len(self.player_count)

    """
    An embed constructor which sends a message to the channel
    """
    def send_message(self, message: str, color: int=EmbedColor.INFO.value):
        print(message)
        pass

    """
    Adds a player to the current game
    """
    def add_player(self, discord_member):
        if discord_member not in self.players:
            self.players.append(discord_member)
            self.send_message(f'{discord_member} joined the game.')
        else:
            self.send_message(f'{discord_member} is already in the game.')
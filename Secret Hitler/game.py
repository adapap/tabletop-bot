from player import Player
from utils import EmbedColor

class Game:
    def __init__(self, *, name: str):
        self.name = name
        self.players = []
        self.channel = None

    """
    Returns the number of players in the game
    """
    @property
    def player_count(self):
        return len(self.players)

    """
    An embed constructor which sends a message to the channel
    """
    def send_message(self, message: str, *, color: int=EmbedColor.INFO, channel: str='public'):
        print(f'({channel}) {message}')
        pass

    """
    Adds a player to the current game
    """
    def add_player(self, discord_member):
        if discord_member not in self.players:
            player = Player(name=discord_member, dm_channel='dm_' + discord_member)
            self.players.append(player)
            self.send_message(f'{discord_member} joined the game.')
        else:
            self.send_message(f'{discord_member} is already in the game.')
from player import Player
from utils import EmbedColor

class Game:
    """
    Game object for each game running through Discord
    """
    def __init__(self, *, name: str):
        self.name = name
        self.players = []
        self.channel = None

    @property
    def player_count(self):
        """
        Returns the number of players in the game
        """
        return len(self.players)

    def send_message(self, message: str, *, color: int=EmbedColor.INFO, channel: str='public'):
        """
        An embed constructor which sends a message to the channel
        """
        print(f'({channel}) {message}')
        pass

    def add_player(self, discord_member):
        """
        Adds a player to the current game
        """
        if discord_member not in self.players:
            player = Player(name=discord_member, dm_channel='dm_' + discord_member)
            self.players.append(player)
            self.send_message(f'{discord_member} joined the game.')
        else:
            self.send_message(f'{discord_member} is already in the game.')
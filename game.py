from utils import EmbedColor

class Game:
    """Game object for each game running through Discord."""
    def __init__(self):
        self.channel = None
        self.players = []

    @property
    def player_count(self):
        """Returns the number of players in the game."""
        return len(self.players)

    def send_message(self, message: str, *, color: int=EmbedColor.INFO, channel: str='public'):
        """An embed constructor which sends a message to the channel."""
        print(f'({channel}) {message}')
        pass
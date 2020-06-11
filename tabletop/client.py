import discord
from .games import GameCollection

class Client:
    """The client that handles running the different games supported by Tabletop."""
    def __init__(self, games: GameCollection):
        self.games = games

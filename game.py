import discord
from discord import Embed

from utils import EmbedColor

class Game:
    """Game object for each game running through Discord."""
    def __init__(self):
        self.channel = None
        self.bot = None
        self.players = []

    @property
    def player_count(self):
        """Returns the number of players in the game."""
        return len(self.players)

    async def send_message(self, description: str, *, title: str=None, color: int=EmbedColor.INFO, channel: discord.TextChannel=None):
        """
        An embed constructor which sends a message to the channel.
        Default channel is the channel in which the game was started.
        """
        if not channel and self.channel is None:
            raise ValueError('No discord channel provided.')
        elif not channel:
            channel = self.channel
        await channel.send(embed=Embed(
            description=description,
            title=title,
            color=color))

    def __repr__(self):
        return f'{self.name}'
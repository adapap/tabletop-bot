import discord
from discord import Embed


from utils import EmbedColor

class Game:
    """Game object for each game running through Discord."""
    def __init__(self):
        self.channel = None
        self.bot = None
        self.players = []
        self.started = False

    @property
    def player_count(self):
        """Returns the number of players in the game."""
        return len(self.players)

    @property
    def player_ids(self):
        """Returns a list of player IDs of the players in the game."""
        return [player.data.id for player in self.players]    

    @property
    def bots(self):
        """Returns a list of players in the game that are bots."""
        return [player.data for player in self.players if player.data.test_player]

    @property
    def bot_count(self):
        """Returns the number of bots in the game."""
        return len(self.bots)

    @property
    def duration(self):
        """Returns the time elapsed since the start of the game."""
        return 1

    def get_player(self, _id):
        """Returns a player object given their ID."""
        try:
            return self.players[self.player_ids.index(_id)]
        except ValueError:
            return None

    async def send_message(self, description: str, *, 
        title: str=None, color: int=EmbedColor.INFO, channel: discord.TextChannel=None, footer=None, fields=None):
        """
        An embed constructor which sends a message to the channel.
        Default channel is the channel in which the game was started.
        """
        if not channel and self.channel is None:
            raise ValueError('No discord channel provided.')
        elif not channel:
            channel = self.channel
        embed = Embed(description=description, title=title, color=color)
        if footer:
            embed.set_footer(text=footer)
        if fields:
            for field in fields:
                embed.add_field(**field)
        await channel.send(embed=embed)

    def __repr__(self):
        return f'{self.name}'
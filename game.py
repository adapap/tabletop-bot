import discord
from discord import Embed
from utils import EmbedColor

import io
from datetime import datetime
from itertools import count
from PIL import Image
from random import sample

class Game:
    """Game object for each game running through Discord."""
    def __init__(self, bot):
        self.channel = None
        self.bot = bot
        self.bots = {}
        self.started = False
        self.game_info = True
        self.asset_folder = ''
        self.start_time = 0

        self.uid_gen = count(-1, -1)
        self.nametag_gen = iter(sample(range(100, 1000), 900))

        self.emojis = {}
        # Emoji Vault A
        VAULT_A = 529174297382748170
        for emoji in bot.get_guild(VAULT_A).emojis:
            self.emojis[emoji.name] = emoji

    @property
    def player_count(self):
        """Returns the number of players in the game."""
        return len(self.players)

    @property
    def player_ids(self):
        """Returns a list of player IDs of the players in the game."""
        return [player.id for player in self.players]

    @property
    def bot_count(self):
        """Returns the number of bots in the game."""
        return len(self.bots)

    @property
    def duration(self):
        """Returns the time elapsed (seconds) since the start of the game."""
        return (datetime.now() - self.start_time).seconds

    async def message(self, description: str='', *, embed=None, file=None,
        title: str=None, color: int=EmbedColor.INFO, channel: discord.TextChannel=None, footer=None, fields=None, image=None):
        """
        An embed constructor which sends a message to the channel.
        Default channel is the channel in which the game was started.
        """
        if not channel and self.channel is None:
            raise ValueError('No discord channel provided.')
        elif not channel:
            channel = self.channel
        if embed and file:
            return await channel.send(embed=embed, file=file)
        embed = Embed(description=description, title=title, color=color)
        if channel != self.channel:
            msg = f'#{self.channel.name} in {self.channel.guild.name}'
            if footer:
                msg = f'{footer} | {msg}'
            embed.set_footer(text=msg)
        elif footer:
            embed.set_footer(text=footer)
        if fields:
            for field in fields:
                embed.add_field(**field)
        if image:
            if type(image) == str:
                image = image_from_bytes(f'{self.asset_folder}{image}')
            file = discord.File(image, filename='image.png')
            embed.set_image(url='attachment://image.png')
            return await channel.send(embed=embed, file=file)
        else:
            return await channel.send(embed=embed)

    async def warn(self, **kwargs):
        """Sends a warning message."""
        await self.message(**kwargs.update({'color': EmbedColor.WARN}))

    async def error(self, **kwargs):
        """Sends an error message."""
        await self.message(**kwargs.update({'color': EmbedColor.ERROR}))

    async def success(self, **kwargs):
        """Sends a success message."""
        await self.message(**kwargs.update({'color': EmbedColor.SUCCESS}))

    async def start_game(self):
        """Subclasses, or games, must implement this method."""
        raise NotImplementedError(f'{self.__class__.__name__} needs a `start_game` method.')

    def __repr__(self):
        return f'{self.name}'
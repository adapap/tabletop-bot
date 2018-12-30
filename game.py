import discord
from discord import Embed


from utils import EmbedColor

class Game:
    """Game object for each game running through Discord."""
    def __init__(self):
        self.channel = None
        self.bot = None
        self.bots = {}
        self.started = False
        self.game_info = True
        self.asset_folder = ''

        self.emojis = {
            1: ':one:',
            2: ':two:',
            3: ':three:',
            4: ':four:',
            5: ':five:',
            6: ':six:',
            7: ':seven:',
            8: ':eight:',
            9: ':nine:',
            0: ':zero:'
        }

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
        """Returns the time elapsed since the start of the game."""
        return 1

    async def send_message(self, description: str='', *, 
        title: str=None, color: int=EmbedColor.INFO, channel: discord.TextChannel=None, footer=None, fields=None, image=None):
        """
        An embed constructor which sends a message to the channel.
        Default channel is the channel in which the game was started.
        """
        if not channel and self.channel is None:
            raise ValueError('No discord channel provided.')
        elif not channel:
            channel = self.channel
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
            image_path = self.asset_folder + image
            file = discord.File(image_path, filename='image.png')
            embed.set_image(url='attachment://image.png')
            return await channel.send(embed=embed, file=file)
        else:
            return await channel.send(embed=embed)

    async def start_game(self):
        """Subclasses, or games, must implement this method."""
        raise NotImplementedError(f'{self.__class__.__name__} needs a `start_game` method.')

    def __repr__(self):
        return f'{self.name}'
import discord
from discord import Embed

from Image import AssetManager, ImageUtil
from Utils import EmbedColor

import asyncio
from datetime import datetime

class Game(AssetManager):
    """Game object for each game running through Discord."""
    def __init__(self, bot, path):
        super().__init__(path)
        self.channel = None
        self.bot = bot
        self.started = False
        self.game_info = True
        self.asset_folder = ''
        self.start_time = 0

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
                      title: str=None, color: int=EmbedColor.INFO, channel: discord.TextChannel=None,
                      footer=None, fields=None, image=None):
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
                image = ImageUtil.from_file(image)
            file = discord.File(image, filename='image.png')
            embed.set_image(url='attachment://image.png')
            return await channel.send(embed=embed, file=file)
        else:
            return await channel.send(embed=embed)

    async def warn(self, description: str='', **kwargs):
        """Sends a warning message."""
        kwargs.update({'color': EmbedColor.WARN})
        await self.message(description, **kwargs)

    async def error(self, description: str='', **kwargs):
        """Sends an error message."""
        kwargs.update({'color': EmbedColor.ERROR})
        await self.message(description, **kwargs)

    async def success(self, description: str='', **kwargs):
        """Sends a success message."""
        kwargs.update({'color': EmbedColor.SUCCESS})
        await self.message(description, **kwargs)

    async def player_join_gui(self, players):
        """An interface for joining, leaving, and adding bots to the game."""
        gui_embed = discord.Embed(title='Players', description='...')
        gui_embed.set_footer(text='Join using the buttons below!')

        gui = await self.channel.send(embed=gui_embed)
        await gui.add_reaction(self.emojis['add_user'])
        await gui.add_reaction(self.emojis['remove_user'])
        await gui.add_reaction(self.emojis['bot'])
        await gui.add_reaction(self.emojis['play'])

        react_check = lambda r, u: r.message.id == gui.id and not u.bot
        while True:
            reaction, user = await self.bot.wait_for('reaction_add', check=react_check)
            await gui.remove_reaction(reaction, user)
            command = reaction.emoji.name
            if command == 'play':
                if not 5 <= len(players) <= 10:
                    await self.error('You must have between 5-10 players to start the game.')
                else:
                    await self.start_game()
                    break
            elif command == 'add_user':
                result = await players.add_player(member=user)
                if not result:
                    await self.warn(f'{user.name} is already in the game.')
                gui_embed.description = '\n'.join(player.name for player in players)
                await gui.edit(embed=gui_embed)
            elif command == 'remove_user':
                result = await players.remove_player(id=user.id)
                if not result:
                    await self.warn(f'You are not currently in the game.')
                gui_embed.description = '\n'.join(player.name for player in players) if len(players) else '...'
                await gui.edit(embed=gui_embed)
            elif command == 'bot' and 'Tabletop Master' in map(lambda r: r.name, user.roles):
                bot_check = lambda m: m.author.id == user.id
                prompt = await self.message('How many bots?')
                msg = await self.bot.wait_for('message', check=bot_check)
                await asyncio.sleep(1)
                await prompt.delete()
                await msg.delete()
                try:
                    num_bots = int(msg.content)
                    if num_bots < 1:
                        for _ in range(abs(num_bots)):
                            if len(players.bots()) == 0:
                                continue
                            await players.remove_player(players.bots()[-1])
                    for _ in range(num_bots):
                        result = await players.add_bot()
                        if not result:
                            await self.warn('Unable to add bot to the game.')
                            break
                    gui_embed.description = '\n'.join(player.name for player in players.players())
                    await gui.edit(embed=gui_embed)
                except ValueError:
                    await self.error('Invalid number.')

    async def on_load(self):
        """Runs when a game is loaded from the selection panel (required method in games)."""
        if self.__class__.__name__ == 'Game':
            raise NotImplementedError(f'{self.__class__.__name__} needs an `on_load` method.')
        load_image = ImageUtil.from_file(self.get_asset(self.load_image)) if self.load_image else None
        await self.success(title=self.name, description=self.load_message, image=load_image)

    async def start_game(self):
        """Subclasses, or games, must implement this method."""
        if self.__class__.__name__ == 'Game':
            raise NotImplementedError(f'{self.__class__.__name__} needs a `start_game` method.')
        self.start_time = datetime.now()

    def __repr__(self):
        return f'{self.name}'
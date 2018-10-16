# Discord
import discord
from discord import Embed
from discord.ext import commands

import asyncio
from game import Game
from utils import EmbedColor

class Cog:
    def __init__(self, bot):
        self.bot = bot
        self.cardbot = bot.cardbot
        self.game = self.cardbot.game

    @commands.command(aliases=['test'])
    async def debug(self, ctx):
        await ctx.send(self.cardbot)

    @commands.command()
    async def join(self, ctx, test_player: str='', repeat: int=1):
        """Joins the current running game."""
        if self.game.started:
            return
        player = ctx.author
        if test_player == 'bot':
            player = None
        for _ in range(repeat):
            await self.game.add_player(player)
            await asyncio.sleep(1)

    @commands.command()
    async def leave(self, ctx):
        """Leaves the current game."""
        if self.game.started:
            await self.game.send_message('add leaving in middle of game... (this will break)')
        player = ctx.author
        await self.game.remove_player(player)

    # Game Commands
    @commands.command()
    async def nominate(self, ctx, player: str=''):
        member = None
        game = self.game
        if not game.started:
            return
        if not game.stage == 'nomination':
            await game.send_message(embed=Embed(description='It is not time to nominate.', color=EmbedColor.WARN))
        elif ctx.author.id != game.president.id:
            await game.send_message(embed=Embed(description='You are not the President.', color=EmbedColor.WARN))
        elif player.startswith('Bot'):
            try:
                member = game.players[[player.data.name for player in game.players].index(player)]
            except ValueError:
                await game.send_message(embed=Embed(description=f'There is no bot named {player}.', color=EmbedColor.ERROR))
        else:
            if len(ctx.message.mentions) != 1:
                await game.send_message('Invalid nomination. @mention the player you would like to nominate.', color=EmbedColor.WARN)
            else:
                member = game.get_player(ctx.message.mentions[0].id)
        await game.send_message(member.name)
        # Logic
        if member == game.prev_president or member == game.prev_chancellor or member.id == ctx.author.id:
            await game.send_message('This player is ineligible to be nominated as Chancellor. Please choose another chancellor.', color=EmbedColor.ERROR)
        else:
            game.nominee = member
            await game.send_message(f'{self.nominee.name} has been nominated to be the Chancellor!')
            game.stage = self.next_stage()
            await game.tick()

def setup(bot):
    bot.add_cog(Cog(bot))
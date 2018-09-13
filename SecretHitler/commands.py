# Discord
import discord
from discord import Embed
from discord.ext import commands

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
    async def join(self, ctx):
        """Joins the current running game."""
        player = ctx.author
        await self.game.add_player(player)

    @commands.command()
    async def leave(self, ctx):
        """Leaves the current game."""
        player = ctx.author
        await self.game.remove_player(player)


def setup(bot):
    bot.add_cog(Cog(bot))
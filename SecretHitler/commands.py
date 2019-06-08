import discord
from discord import Embed
from discord.ext import commands
import asyncio

class SecretHitler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game = self.bot.game

    @commands.command()
    async def join(self, ctx, bot: str='', repeat: int=1):
        """Joins the current running game."""
        await ctx.message.delete()
        if self.game.started:
            await self.game.error(f'You cannot join a game already running.')
            return
        for _ in range(repeat):
            member = ctx.author
            if bot == 'bot':
                await self.game.add_bot()
            else:
                await self.game.add_player(member)

    @commands.command()
    async def leave(self, ctx, bot_name: str=None):
        """Leaves the current game."""
        await ctx.message.delete()
        if self.game.started:
            self.game.started = False
            await self.game.message('Game terminated due to player leaving the game.')
        if bot_name:
            await self.game.remove_player(name=bot_name)
        else:
            await self.game.remove_player(id=ctx.author.id)

def setup(bot):
    bot.add_cog(SecretHitler(bot))
# Discord
import discord
from discord import Embed
from discord.ext import commands

@commands.command(cls=commands.Command)
async def hello(ctx):
    await ctx.send('hello')



command_list = set([
    hello
])
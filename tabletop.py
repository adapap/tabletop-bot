# Discord
import discord
from discord import Embed
from discord.ext import commands

# Python Lib
import asyncio
import ast
import json
import os
import re
import sys
import traceback
from importlib import import_module

# Custom
from game import Game
from utils import *

class Cardbot(commands.Bot):
    """Handles the setup and instancing of different games."""
    games = {}
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = None

        rootdir = os.getcwd()
        ignore_dirs = ['.git', '__pycache__', 'base_assets']

        # Import all game folders, import them, and store their classes
        for d in os.listdir(rootdir):
            if os.path.isdir(os.path.join(rootdir, d)) and d not in ignore_dirs:
                game_name = self.to_snake_case(d)
                import_module(f'{d}.{game_name}', package='tabletop')
                game_class = getattr(sys.modules[f'{d}.{game_name}'], d)
                self.games[d] = game_class

    @property
    def game_list(self):
        """Shows a list of all available games."""
        return [game for game in self.games.keys()]

    def load_game(self, name: str):
        """Returns the class object for the game."""
        if name not in self.game_list:
            raise KeyError(f'Cardbot does not support the game: {name}')
        self.game = self.games[name](bot)
        return self.game

    def to_snake_case(self, s: str):
        """Converts CamelCase to snake_case."""
        camel_case = [x.group(0).lower() for x in re.finditer(r'.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', s)]
        return '_'.join(camel_case)

    def __repr__(self):
        return f'<Active Game: {self.game}>'


bot = Cardbot(command_prefix='$', description='''A discord tabletop bot.''')
bot.remove_command('help')

def has_role(self, rolename):
    """Returns a boolean whether a member has a role."""
    return rolename in [role.name for role in self.roles]
discord.Member.has_role = has_role

@bot.command(aliases=['test'])
async def debug(ctx, *params: lower):
    """General purpose test command."""
    img = 'loading.gif'
    asset_path = 'SecretHitler/assets/'
    image_path = 'SecretHitler/assets/' + img
    file = discord.File(image_path, filename=img)
    embed = discord.Embed(description='Loading!')
    embed.set_author(name='Loading?', icon_url=f'attachment://{img}')
    await ctx.send(embed=embed, file=file)

@commands.guild_only()
@bot.command(aliases=['purge', 'del', 'delete'])
async def clear(ctx, number=1):
    """Removes the specified number of messages."""
    if ctx.author.has_role('Staff'):
        return
    number = int(number)
    await ctx.message.delete()
    if number > 99:
        await ctx.send('Must be between 1-99.')
        await asyncio.sleep(2.5)
        await ctx.channel.purge(limit=1, check=lambda m: m.author == ctx.author)
        return
    await ctx.channel.purge(limit=number)

def insert_returns(body):
    """Helper function for _eval command."""
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

@bot.command(aliases=['$'])
async def _eval(ctx, *, cmd):
    """Evaluates input for test purposes."""
    eval_users = {
        153980025601916928: 'adapap',
        273189886981570560: 'Discord Bot Test',
        133230770876710912: 'flipthebit'
    }
    if ctx.author.id not in eval_users:
        return
    await ctx.message.delete()
    fn_name = "_eval_expr"
    cmd = cmd.strip("` ")
    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
    body = f"async def {fn_name}():\n{cmd}"
    parsed = ast.parse(body)
    body = parsed.body[0].body
    insert_returns(body)
    env = {
        'bot': ctx.bot,
        'discord': discord,
        'game': bot.game,
        'commands': commands,
        'ctx': ctx,
        '__import__': __import__
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)
    try:
        result = await eval(f"{fn_name}()", env)
        color = EmbedColor.INFO
    except Exception as e:
        result = e
        color = EmbedColor.ERROR
    await ctx.send(embed=Embed(title=f'○{" " * 150}○', description=f':inbox_tray:\n```python\n{cmd[4:]}```\n:outbox_tray:\n```python\n{result}```', color=color))

@bot.command(aliases=['game_list', 'gamelist'])
async def games(ctx):
    """Returns a list of available games to play."""
    game_list = '\n'.join([x().name for x in bot.games.values()])
    await ctx.send(embed=Embed(title='Games', description=game_list, color=EmbedColor.INFO))

@bot.command(aliases=['load'])
async def load_game(ctx, *game_name: str):
    """Loads the game for players to join and configures player joining."""
    # If a game is already running, unload it first.
    if bot.game:
        await ctx.invoke(unload_game)
    game_name = ' '.join(game_name)
    default = ''
    # DEFAULT GAME
    if game_name == '':
        default = '(default) '
        game_name = 'Secret Hitler'
    name = re.sub(r'\s*', '', game_name)
    if name not in bot.games:
        await ctx.send(embed=Embed(title=f'The game {game_name} is not available.', color=EmbedColor.ERROR))
        return
    game = bot.load_game(name)
    game.channel = ctx.message.channel
    assert hasattr(game, 'on_load')
    try:
        bot.load_extension(f'{name}.commands')
    except Exception as e:
        print(f'Failed to load extension for {game_name}.', file=sys.stderr)
        traceback.print_exc()
    msg = f'{game_name} loaded!'
    # await game.send_message(game.load_message, title=msg, color=EmbedColor.SUCCESS, image=game.load_image)
    await on_load()
    print(msg)

@bot.command(aliases=['start'])
async def start_game(ctx):
	await bot.game.start_game()

@bot.command(aliases=['unload'])
async def unload_game(ctx):
    """Removes all commands and unloads the current game."""
    if not bot.game:
        await ctx.send(embed=Embed(title=f'There is no game running. Use `$load [game]` to start a game.', color=EmbedColor.WARN))
        return
    game_name = bot.game.name
    name = re.sub(r'\s*', '', game_name)
    try:
        bot.unload_extension(f'{name}.commands')
        bot.game = None
    except Exception as e:
        print(f'Unloading failed.', file=sys.stderr)
        traceback.print_exc()
    msg = f'{game_name} has been unloaded.'
    await ctx.send(embed=Embed(title=msg, color=EmbedColor.INFO))
    print(msg)

async def on_load():
    """Starts the current game through the game's start_game method."""
    await bot.change_presence(activity=discord.Game(name=bot.game.name))
    await bot.game.on_load()

@bot.event
async def on_ready():
    """Runs when Discord bot logs in."""
    message = 'Logged in as %s.' % bot.user
    uid_message = 'User id: %s.' % bot.user.id
    separator = '━' * max(len(message), len(uid_message))
    print(separator)
    try:
        print(message)
    except:
        print(message.encode(errors='replace').decode())
    print(uid_message)
    print('Prefix:', '$')
    print(separator)
    await bot.change_presence(activity=discord.Game(name='tabletop games!'))

@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return

    error = getattr(error, 'original', error)
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.BotMissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
        await ctx.send(_message)
        return

    if isinstance(error, commands.MissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
        await ctx.send(_message)
        return

    error_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    await ctx.send(embed=Embed(title=f'{type(error).__name__}', description=f'```python\n{error_str[-2000:]}```', color=EmbedColor.ERROR))
    print(error_str)

if __name__ == '__main__':
    with open('token.json') as file:
        data = json.loads(file.read())
        token = data['token']

    bot.run(token)
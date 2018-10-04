# Discord
import discord
from discord import Embed
from discord.ext import commands

# Python Lib
import ast
import json
import os
import re
import sys
from importlib import import_module

# Custom
from game import Game
from utils import EmbedColor, LinkedList

class Cardbot:
    """Handles the setup and instancing of different games."""
    games = {}
    def __init__(self):
        self.game = None

        rootdir = os.getcwd()
        ignore_dirs = ['.git', '__pycache__', 'cardbot-env']

        # Import all game folders, import them, and store their classes
        for d in os.listdir(rootdir):
            if os.path.isdir(os.path.join(rootdir, d)) and d not in ignore_dirs:
                game_name = self.to_snake_case(d)
                import_module(f'{d}.{game_name}', package='cardbot')
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
        self.game = self.games[name]()
        return self.game

    def to_snake_case(self, s: str):
        """Converts CamelCase to snake_case."""
        camel_case = [x.group(0).lower() for x in re.finditer(r'.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', s)]
        return '_'.join(camel_case)

    def __repr__(self):
        return f'<Active Game: {self.game}>'

bot = commands.Bot(command_prefix='$', description='''A discord tabletop bot.''')
bot.remove_command('help')


def has_role(self, rolename):
    """Returns a boolean whether a member has a role."""
    return rolename in [role.name for role in self.roles]
discord.Member.has_role = has_role


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
        'game': bot.cardbot.game,
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


@bot.command(aliases=['game_list'])
async def games(ctx):
    """Returns a list of available games to play."""
    game_list = '\n'.join([x().name for x in cardbot.games.values()])
    await ctx.send(embed=Embed(title='Games', description=game_list, color=EmbedColor.INFO))


@bot.command(aliases=['load'])
async def load_game(ctx, *game_name: str):
    """Loads the game for players to join and configures player joining."""
    game_name = ' '.join(game_name)
    default = ''
    # DEFAULT GAME
    if game_name == '':
        default = '(default) '
        game_name = 'Secret Hitler'
    name = re.sub(r'\s*', '', game_name)
    if name not in cardbot.games:
        await ctx.send(embed=Embed(title=f'The game {game_name} is not available.', color=EmbedColor.ERROR))
        return
    game = cardbot.load_game(name)
    game.channel = ctx.message.channel
    assert hasattr(game, 'start_game')
    try:
        bot.load_extension(f'{name}.commands')
    except Exception as e:
        print(f'Failed to load extension for {game_name}.', file=sys.stderr)
        traceback.print_exc()
    await ctx.send(embed=Embed(title=f'{default}{game_name} loaded.', color=EmbedColor.SUCCESS))

@bot.command(aliases=['start'])
async def start_game(ctx):
    """Starts the current game through the game's start_game method."""
    await cardbot.game.start_game()

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
    await bot.change_presence(activity=discord.Game(name='Tabletop Bot'))


if __name__ == '__main__':
    cardbot = Cardbot()
    bot.cardbot = cardbot

    with open('token.json') as file:
        data = json.loads(file.read())
        token = data['token']

    bot.run(token)
# This file is executed when running 'tabletop' as a module
import argparse
import asyncio
import tabletop
from .games import GameCollection
from .games.TheMind import TheMind
from .views.console import ConsoleView

games = [TheMind]

description = """Tabletop is a bot that allows you to play board, card, and other
tabletop games with your friends through interfaces such as Discord."""
parser = argparse.ArgumentParser(prog='tabletop', description=description)
parser.add_argument('-v', '--view', help='The interface to handle I/O. Default is "discord".',
    choices=['console', 'discord'], default='discord')
args = parser.parse_args()

if args.view == 'console':
    view = ConsoleView()
client = tabletop.Client(view, games)
loop = asyncio.get_event_loop()
loop.run_until_complete(client.connect())

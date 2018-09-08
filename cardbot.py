import discord
import os
import re
import sys
from importlib import import_module

from game import Game
from utils import EmbedColor, LinkedList

class Cardbot:
    """Handles the setup and instancing of different games."""
    games = {}
    def __init__(self):
        self.active_game = None

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
        self.active_game = name
        return self.games[name]()

    def to_snake_case(self, s: str):
        """Converts CamelCase to snake_case."""
        camel_case = [x.group(0).lower() for x in re.finditer(r'.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', s)]
        return '_'.join(camel_case)

    def __repr__(self):
        return f'<Active Game: {self.active_game}>'

if __name__ == '__main__':
    cardbot = Cardbot()
    print(cardbot.game_list)
    game = cardbot.load_game('SecretHitler')
    # game.start_game()
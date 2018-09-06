import os
import re
from importlib import import_module

from game import Game
from utils import EmbedColor, LinkedList

class Cardbot:
    """
    Handles the setup and instancing of different games
    """
    def __init__(self):
        rootdir = os.getcwd()
        ignore_dirs = ['.git', '__pycache__', 'cardbot-env']

        for d in os.listdir(rootdir):
            if os.path.isdir(os.path.join(rootdir, d)) and d not in ignore_dirs:
                import_module(f'{d}.secret_hitler')

    def to_snake_case(self, s: str=None):
        x = re.split(r'[A-Z]\s*', s)
        print(x)

if __name__ == '__main__':
    cardbot = Cardbot()
    print(secret_hitler)

# game = SecretHitler(name='Secret Hitler')
# game.start_game()
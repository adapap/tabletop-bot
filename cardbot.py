import os
from importlib import import_module

rootdir = os.getcwd()
ignore_dirs = [".git", "__pycache__", "cardbot-env"]

for d in os.listdir(rootdir):
    if os.path.isdir(os.path.join(rootdir, d)) and d not in ignore_dirs:
        import_module(f'{d}.secret_hitler', package='cardbot')

game = SecretHitler(name='Secret Hitler')
game.start_game()
from PIL import Image
import io
from utils import *

class Temp:
    def __init__(self):
        self.asset_folder = 'assets/'
        self.board = {
        'fascist': 0,
        'liberal': 5
        }
        self.player_count = 5

    def run(self):

        liberal_board = Image.open(f'{self.asset_folder}liberal_board.png').convert('RGBA')
        players = self.player_count
        if players <= 6:
            fascist_board = Image.open(f'{self.asset_folder}fascist_board_56.png').convert('RGBA')
        elif players <= 8:
            fascist_board = Image.open(f'{self.asset_folder}fascist_board_78.png').convert('RGBA')
        elif players <= 10:
            fascist_board = Image.open(f'{self.asset_folder}fascist_board_910.png').convert('RGBA')

        liberal_policy = Image.open(f'{self.asset_folder}liberal_policy.png').convert('RGBA')
        fascist_policy = Image.open(f'{self.asset_folder}fascist_policy.png').convert('RGBA')
        w, h = liberal_policy.size
        ratio = 112 / h
        size = (int(w * ratio), int(h * ratio))

        liberal_policy.thumbnail(size, Image.ANTIALIAS)
        fascist_policy.thumbnail(size, Image.ANTIALIAS)

        left = 95
        top = 54
        offset = 95
        for i in range(self.board['liberal']):
            pos = (left + offset * i, top)
            liberal_board.paste(liberal_policy, pos)
        left = 51
        offset = 93
        for i in range(self.board['fascist']):
            pos = (left + offset * i, top)
            fascist_board.paste(fascist_policy, pos)
        liberal = io.BytesIO()
        liberal_board.save(liberal, format='PNG')
        liberal = liberal.getvalue()
        fascist = io.BytesIO()
        fascist_board.save(fascist, format='PNG')
        fascist = fascist.getvalue()

        board = image_merge(liberal, fascist, axis=1)
        im = Image.open(io.BytesIO(board))
        im.show()

Temp().run()
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Card import Deck
from Game import Game
from Image import ImageUtil
from Player import PlayerCycle
from Utils import EmbedColor

class Poker(Game):
    """Poker is a card game."""
    pass
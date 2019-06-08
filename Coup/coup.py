import os
import sys

from .cards import Duke, Assassin, Captain, Ambassador, Contessa
from .player import Player

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Card import Deck
from Game import Game
from Player import PlayerCycle
from Utils import EmbedColor

class Coup(Game):
    name = 'Coup'
    load_message = """
In the not too distant future, the government is run for profit by a new \
“royal class” of multinational CEOs. Their greed and absolute control of \
the economy has reduced all but a privileged few to lives of poverty and \
desperation. Out of the oppressed masses rose The Resistance, an underground \
organization focused on overthrowing these powerful rulers. The valiant \
efforts of The Resistance have created discord, intrigue and weakness in the \
political courts of the noveau royal, bringing the government to brink of \
collapse. But for you, a powerful government official, this is your opportunity \
to manipulate, bribe and bluff your way into absolute power. To be successful, \
you must destroy the influence of your rivals and drive them into exile. \
In these turbulent times there is only room for one to survive.
"""
    load_image = ''

    def __init__(self, bot):
        super().__init__(bot, __file__)
        self.player_cycle = PlayerCycle(Player)

        self.treasury = 0
        self.rules = ''

    @property
    def players(self):
        """Returns a list of players in the game."""
        return self.player_cycle.players()

    async def setup(self):
        """Sets up the game by distributing cards and coins."""
        self.deck = Deck()
        self.deck.insert(Duke, 3)
        self.deck.insert(Assassin, 3)
        self.deck.insert(Captain, 3)
        self.deck.insert(Ambassador, 3)
        self.deck.insert(Contessa, 3)
        self.deck.shuffle()
        self.stockpile = Deck()

        for player in self.players:
            player.cards.extend(self.deck.top(2))
            player.coins = 2

    async def on_load(self):
        await super().on_load()
        await self.player_join_gui(self.player_cycle)

    async def start_game(self):
        await super().on_start()
        await self.setup()
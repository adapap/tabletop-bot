import discord

from Player import BasePlayer

class Player(BasePlayer):
    def __init__(self, *, member: discord.Member):
        super().__init__(member)
        self.identity = None
        self.voted = False
        self.veto = False
        self.last_president = False
        self.last_chancellor = False
        self.investigated = False

    @property
    def had_position(self):
        return self.last_president or self.last_chancellor
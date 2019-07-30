import discord

from Player import BasePlayer

class Player(BasePlayer):
    def __init__(self, *, member: discord.Member):
        super().__init__(member)
        self.cards = []
        self.coins = 0
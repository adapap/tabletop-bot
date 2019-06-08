import discord

from Player import BasicPlayer

class Player(BasicPlayer):
    def __init__(self, *, member: discord.Member):
        super().__init__(member)
        self.cards = []
        self.coins = 0
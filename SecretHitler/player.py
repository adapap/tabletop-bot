import discord
from itertools import count
from random import randint

uid_gen = count(-1, -1)

class Player:
    def __init__(self, *, member: discord.Member=None):
        if member is None:
            self.name = f'Player{randint(100, 999)}'
            self.id = next(uid_gen)
            self.dm_channel = None
            self.test = True
        else:
            self.name = member.display_name
            self.id = member.id
            self.dm_channel = member.dm_channel
            self.test = False
        self.identity = None
        self.voted = False
        self.veto = False
        self.last_president = False
        self.last_chancellor = False
        self.investigated = False

    @property
    def had_position(self):
        return self.last_president or self.last_chancellor

    def __repr__(self):
        return f'<Player: {self.name}>'
import discord
from itertools import count
from random import sample

uid_gen = count(-1, -1)
nametag_gen = iter(sample(range(100, 1000), 900))

class Player:
    def __init__(self, *, member: discord.Member=None, dm_channel=None):
        if member is None:
            self.name = f'Bot{next(nametag_gen)}'
            self.id = next(uid_gen)
            self.dm_channel = dm_channel
            self.test_player = True
        else:
            self.name = member.display_name
            self.id = member.id
            self.dm_channel = dm_channel
            self.test_player = False
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

    def __str__(self):
        return self.name
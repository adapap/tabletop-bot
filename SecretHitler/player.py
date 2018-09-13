import discord

class Player:
    def __init__(self, *, member: discord.Member):
        self.name = member.display_name
        self.id = member.id
        self.dm_channel = member.dm_channel
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
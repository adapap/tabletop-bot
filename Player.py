import discord
from itertools import count
from random import choice, sample

class BasicPlayer:
    """An abstract player class to be modified by individual games."""
    def __init__(self, member: discord.Member):
        self.member = member
        self.name = member.display_name
        self.fullname = member.display_name if member.bot else member.name
        self.id = member.id
        self.dm_channel = member.dm_channel
        self.bot = member.bot

        self.next = None
        self.prev = None

    async def message(self, content, **kwargs):
        """Sends a message to the dm_channel of the member."""
        if self.dm_channel: # Custom channel specified for bots
            await self.dm_channel.send(content, **kwargs)

    def __repr__(self):
        return f'<Player: {self.name}>'

    def __str__(self):
        return self.name

class PlayerCycle:
    """Turn manager which uses a circular player order."""
    def __init__(self, player_cls):
        self.head = None
        self.tail = None
        self.num_players = 0

        self.player_cls = player_cls
        self.uid_gen = count(-1, -1)
        self.nametag_gen = iter(sample(range(100, 1000), 900))

    def players(self, *, filter_=None):
        """Returns a list of all players in the cycle (optionally filtered)."""
        players = []
        player = self.head
        for _ in range(self.num_players):
            if filter_ and not filter_(player):
                continue
            players.append(player)
            player = player.next
        return players

    def bots(self):
        """Returns a list of all bot players in the cycle."""
        return self.players(filter_=lambda p: p.bot)

    def random_player(self):
        """Selects a random player from the cycle."""
        return choice(self.players())

    async def add_player(self, *, member: discord.Member):
        """Adds a player to the cycle."""
        if not member.bot:
            await member.create_dm()
        node = self.player_cls(member=member)
        if node in self.players():
            return False
        if self.head is None:
            node.next = node
            node.prev = node
            self.head = node
            self.tail = node
        else:
            node.prev = self.tail
            node.next = self.head
            self.tail.next = node
            self.tail = node
            self.head.prev = self.tail
        self.num_players += 1
        return True

    async def add_bot(self, *, dm_channel: discord.TextChannel=None):
        """Adds a bot to the cycle."""
        member = discord.Object(id=str(next(self.uid_gen)))
        member.display_name = f'Bot{next(self.nametag_gen)}'
        member.dm_channel = dm_channel
        member.bot = True
        return await self.add_player(member=member)

    async def remove_player(self, obj=None, **criteria):
        """Removes a player matching criteria."""
        player = self.head
        for _ in range(self.num_players):
            if (obj and obj == player) or all(getattr(player, k) == v for k, v in criteria.items()):
                if self.num_players == 1:
                    self.head = None
                    self.tail = None
                else:
                    player.prev.next = player.next
                    player.next.prev = player.prev
                self.num_players -= 1
                return True
            player = player.next
        return False
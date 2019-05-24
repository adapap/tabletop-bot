import discord
from itertools import count
from random import choice, sample

class BasicPlayer:
    """An abstract player class to be modified by individual games."""
    def __init__(self, member: discord.Member):
        self.name = member.display_name
        self.fullname = member.name
        self.id = member.id
        self.dm_channel = member.dm_channel
        self.bot = member.bot

        self.next = None
        self.prev = None

    def __repr__(self):
        return f'<Player: {self.name}>'

    def __str__(self):
        return self.name

class PlayerCycle:
    """Turn manager which uses a circular player order."""
    def __init__(self, class_):
        self.head = None
        self.tail = None
        self.num_players = 0

        self.class_ = class_
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

    def random_player(self):
        """Selects a random player from the cycle."""
        return choice(self.players())

    async def add_player(self, *, member: discord.Member):
        """Adds a player to the cycle."""
        if not member.bot:
            await member.create_dm()
        node = self.class_(member=member)
        if node in self.players():
            return False
        if self.head == None:
            self.head = node
            self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.num_players += 1
        return True

    async def add_bot(self):
        """Adds a bot to the cycle."""
        member = discord.Object(id=str(next(self.uid_gen)))
        member.display_name = f'Bot{next(self.nametag_gen)}'
        member.dm_channel = None
        member.bot = True
        return await self.add_player(member=member)

    async def remove_player(self, **criteria):
        """Removes a player matching criteria."""
        player = self.head
        for _ in range(self.num_players):
            if all(getattr(player, k) == v for k, v in criteria.items()):
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
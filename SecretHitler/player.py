class Player:
    def __init__(self, *, name: str, dm_channel: str):
        self.name = name
        self.dm_channel = dm_channel
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
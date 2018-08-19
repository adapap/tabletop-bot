class Player:
    def __init__(self, *, name: str, dm_channel: str):
        self.name = name
        self.dm_channel = dm_channel
        self.identity = None
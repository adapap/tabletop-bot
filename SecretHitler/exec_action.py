from random import choice

async def investigate_loyalty(self):
    """The President discovers another player's identity."""
    await self.send_message('The President must investigate another player\'s identity!')
    # Should be replaced with actual choosing procedure
    valid = set(self.players) - set([self.president])
    for investigated_player in self.previously_investigated:
        valid -= set([investigated_player])
    suspect = choice(list(valid))

    while suspect in self.previously_investigated or suspect == self.president:
        await self.send_message('You may not investigate yourself or a previously investigated player!', color=EmbedColor.ERROR)
        suspect = choice(list(valid))

    self.previously_investigated.append(suspect)
    suspect_role = suspect.identity
    if suspect_role == 'Hitler':
        suspect_role = 'Fascist'

    await self.send_message(f'{suspect.name} is a {suspect_role}', channel=self.president.dm_channel, footer=self.president.name)

async def policy_peek(self):
    """The President sees the next three policy cards."""
    await self.send_message('The President will now peek at the top three policies in the deck!')

async def special_election(self):
    """The President elects a new President."""
    await self.send_message('The President must choose another player to be President!')
    valid = set(self.players) - set([self.president])
    nominee = choice(list(valid))
    while nominee == self.president:
        self.send_message('You may not choose yourself!')
        nominee = choice(list(valid))
    self.special_president = nominee
    self.special_election = True

async def execution(self):
    """The President executes a player."""
    valid = [node for node in self.player_nodes if node.data != self.president]
    victim = choice(valid)
    self.player_nodes.remove(victim)
    return victim.data
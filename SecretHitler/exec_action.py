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
    await self.send_message(f'{self.policy_deck[0].card_type}, {self.policy_deck[1].card_type}, {self.policy_deck[2].card_type}',
        channel=self.president.dm_channel)

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
    await self.send_message('The President must now execute a player!')
    # Should be replaced with actual choosing procedure
    valid = set(self.players) - set([self.president])
    victim = choice(list(valid))

    while victim == self.president:
        await self.send_message('You may not execute yourself!', color=EmbedColor.ERROR)
        victim = choice(list(valid))

    self.player_nodes.remove(victim)
    return victim
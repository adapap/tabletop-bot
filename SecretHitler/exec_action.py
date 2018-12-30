from random import choice

async def investigate_loyalty(self):
    """The President discovers another player's identity."""
    """The President elects a new President."""
    valid = [node for node in self.player_nodes if node.data != self.president and not node.data in self.previously_investigated]
    suspect = choice(valid)
    return suspect.data

async def policy_peek(self):
    """The President sees the next three policy cards."""
    await self.send_message('The President will now peek at the top three policies in the deck!')

async def special_election(self):
    """The President elects a new President."""
    valid = [node for node in self.player_nodes if node.data != self.president]
    new_president = choice(valid)
    return new_president.data

async def execution(self):
    """The President executes a player."""
    valid = [node for node in self.player_nodes if node.data != self.president]
    victim = choice(valid)
    self.player_nodes.remove(victim)
    return victim.data
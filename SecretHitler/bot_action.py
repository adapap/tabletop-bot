from random import choice, sample

# General Gameplay
def choose_chancellor(valid):
    """Bot function: Chooses a random chancellor to elect."""
    return choice(valid)

def vote():
    """Bot function: Either votes Ja or Nein."""
    return choice(['ja', 'nein'])

def select_policies(policies):
    """Bot function: Choose two random policies to send to the Chancellor."""
    return sample(policies, 2)

def enact_policy(policies):
    """Bot function: Chooses a random policy to enact."""
    return choice(policies)

def veto():
    """Bot function: Determines if a policy should be vetoed or not."""
    return choice([True, False])

# Executive Action
def investigate_loyalty(game):
    """The President discovers another player's identity."""
    return choice([p for p in game.players if p != game.president and p not in game.previously_investigated])

def special_election(game):
    """The President elects a new President."""
    return choice([p for p in game.players if p != game.president])

def execution(game):
    """The President executes a player."""
    return choice([p for p in game.players if p != game.president])
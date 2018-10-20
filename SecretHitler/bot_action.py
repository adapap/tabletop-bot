from random import choice, sample

def choose_chancellor(valid):
    """Bot function: Chooses a random chancellor to elect."""
    return choice(valid)

def vote():
    """Bot function: Either votes Ja or Nein."""
    return choice(['ja', 'nein'])

def send_policies(policies):
    """Bot function: Choose two random policies to send to the Chancellor."""
    return sample(policies, 2)

def enact(policies):
    """Bot function: Chooses a random policy to enact."""
    return choice(policies)

def veto():
    """Bot function: Determines if a policy should be vetoed or not."""
    return choice([True, False])
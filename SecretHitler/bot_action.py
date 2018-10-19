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

def get_enacted_policy(chosen_policies):
    """Handles getting the Chancellor's chosen policy. Is a dummy function that just chooses a random policy now."""
    return choice(chosen_policies)

def wants_to_veto():
    """Bot function: Determines if a policy should be vetoed or not."""
    return choice([True, False])
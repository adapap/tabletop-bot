from random import choice, sample

class Bot:
    @staticmethod
    def choose_chancellor(valid):
        """Bot function: Chooses a random chancellor to elect."""
        return choice(valid)

    @staticmethod
    def vote():
        """Bot function: Either votes Ja or Nein."""
        return choice(['ja', 'nein'])

    @staticmethod
    def send_policies(self, policies):
        """Bot function: Choose two random policies to send to the Chancellor."""
        return sample(policies, 2)

    @staticmethod
    def get_enacted_policy(self, chosen_policies):
        """Handles getting the Chancellor's chosen policy. Is a dummy function that just chooses a random policy now."""
        return choice(chosen_policies)

    @staticmethod
    def wants_to_veto(self):
        return choice([True, False])
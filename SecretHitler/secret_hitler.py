# Base Modules
from .cards import *
from .player import Player

# Parent Modules
import discord
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import Game
from utils import EmbedColor, LinkedList

from itertools import cycle
from random import shuffle, choice, sample

# Temporary modules
from string import ascii_uppercase as alphabet
from time import sleep


class SecretHitler(Game):
    """Secret Hitler is a card game."""
    name = 'Secret Hitler'
    def __init__(self):
        super().__init__()

        # Adding test players, should replace with a proper player join mechanic
        # Just add to linkedlist and rewrite all the stuffs...
        self.players = LinkedList()
        # for x in alphabet[:8]:
        #     self.add_player(x)
        # Starting player is the first one that joined
        self.player = self.players.head

        # Keeps track of enacted policies
        self.board = {
            'fascist': 0,
            'liberal': 0
        }

        # Create an iterator that cycles every game loop (when action is valid)
        # For example, "election" can be a stage
        self.stages = cycle(['nomination', 'election', 'president', 'chancellor', 'summary'])
        self.next_stage = lambda: next(self.stages)
        self.stage = self.next_stage()

        self.chancellor_rejections = 0
        self.chancellor = None
        self.president = None
        self.prev_president = None
        self.prev_chancellor = None
        self.nominee = None
        self.candidate_policies = None
        self.special_president = None
        self.special_election = False
        self.do_exec_act = False
        self.previously_investigated = []
        self.generate_deck()

        self.rounds = 0

    @property
    def player_list(self):
        """Property that returns a list of players."""
        return self.players.elements


    @property
    def policy_count(self):
        """Property which gives number of policy cards in the deck."""
        return len(self.policy_deck)

    @property
    def next_player(self):
        """Returns the next player in the game."""
        self.player = self.player.next
        return self.player.data

    async def add_player(self, discord_member: discord.Member):
        """Adds a player to the current game."""
        if not self.players.find(discord_member.id, attr='id'):
            player = Player(member=discord_member)
            self.players.add(player)
            await self.send_message(f'{discord_member} joined the game.')
        else:
            await self.send_message(f'{discord_member} is already in the game.', color=EmbedColor.WARN)

    async def remove_player(self, discord_member: discord.Member):
        """Removes a player from the game cycle."""
        player = self.players.find(discord_member.id, attr='id')
        if not player:
            await self.send_message(f'You are not in the current game.', color=EmbedColor.ERROR)
        else:
            self.players.remove(player)
            await self.send_message(f'{discord_member} left the game.')

    def generate_deck(self):
        """Generates a deck of policy cards."""

        # There are 6 fascist policies and 11 liberal policies in a deck
        # If the deck is emptied, reshuffle the deck without the board cards
        self.policy_deck = []
        self.policy_deck.extend([PolicyCard(card_type='fascist', img_src='')] * (11 - self.board['fascist']))
        self.policy_deck.extend([PolicyCard(card_type='liberal', img_src='')] * (6 - self.board['liberal']))
        shuffle(self.policy_deck)


    @property  
    def valid_chancellors(self):
        """Returns a list of valid chancellor nominees."""
        valid = []
        for player in self.player_list:
            if player != self.president and not player.last_chancellor and not (player.last_president and self.player_count > 5):
                valid.append(player)
        return valid

    def choose_chancellor(self):
        """Handles nominating a chancellor. Is a dummy function that just chooses a random player right now."""
        valid = self.valid_chancellors
        return choice(valid)

    def get_voting_results(self):
        """Handles getting voting results. Is a dummy function that just returns true/false right now."""
        return choice([True, False])

    def pick_chosen_policies(self, policies):
        """Handles getting the President's chosen policies. Is a dummy function that just chooses two random policies now."""
        return sample(policies, 2)

    def get_enacted_policy(self, chosen_policies):
        """Handles getting the Chancellor's chosen policy. Is a dummy function that just chooses a random policy now."""
        return choice(chosen_policies)

    def wants_to_veto(self):
        return(choice([True, False]))

    def executive_action(self): 
        """Manages the executive actions that the President must do after a fascist policy is passed."""

        # Executive Action - Investigate Loyalty
        if (self.board['fascist'] == 1 and self.player_count > 8) or (self.board['fascist'] == 2 and self.player_count > 6):
            self.send_message('The President must investigate another player\'s identity!')

            # Should be replaced with actual choosing procedure
            valid = set(self.player_list) - set([self.president])
            for investigated_player in self.previously_investigated:
                valid -= set([investigated_player])
            suspect = choice(list(valid))

            while suspect in self.previously_investigated or suspect == self.president:
                self.send_message('You may not investigate yourself or a previously investigated player!', color=EmbedColor.ERROR)
                suspect = choice(list(valid))

            self.previously_investigated.append(suspect)
            suspect_role = suspect.identity
            if suspect_role == 'Hitler':
                suspect_role = 'Fascist'

            self.send_message(f'{suspect.name} is a {suspect_role}', channel=self.president.dm_channel)

        # Executive Action - Policy Peek
        elif self.board['fascist'] == 3 and self.player_count < 7:
            self.send_message('The President will now peek at the top three policies in the deck!')
            self.send_message(f'{self.policy_deck[0].card_type}, {self.policy_deck[1].card_type}, {self.policy_deck[2].card_type}', channel=self.president.dm_channel)

        # TODO: Executive Action - Special Election
        elif self.board['fascist'] == 3 and self.player_count > 7:
            self.send_message('The President must choose another player to be President!')
            valid = set(self.player_list) - set([self.president])
            nominee = choice(list(valid))
            while nominee == self.president:
                self.send_message('You may not choose yourself!')
                nominee = choice(list(valid))
            self.special_president = nominee
            self.special_election = True

        # Executive Action - Execution
        elif self.board['fascist'] == 4 or self.board['fascist'] == 5:
            self.send_message('The President must now execute a player!')

            # Should be replaced with actual choosing procedure
            valid = set(self.player_list) - set([self.president])
            victim = choice(list(valid))

            while victim == self.president:
                self.send_message('You may not execute yourself!', color=EmbedColor.ERROR)
                victim = choice(list(valid))

            self.players.remove(victim)
            if victim.identity == 'Hitler':
                self.send_message(f'{victim.name} was executed. As he was Hitler, the Liberals win!')
                return -1
            self.send_message(f'{victim.name} was executed.')

        return 0

    def tick(self):
        """Handles the turn-by-turn logic of the game."""
        if self.stage == 'nomination':
            self.president = self.special_president if self.special_election else self.next_player
            self.special_election = False
            self.send_message(f'{self.president.name} is the President now! They must nominate a Chancellor.')

            # Rewrite this into proper chancellor choosing function
            self.nominee = self.choose_chancellor()
            while self.nominee == self.prev_president or self.nominee == self.prev_chancellor:
                self.send_message('This player is ineligible to be nominated as Chancellor. Please choose another chancellor.', color=EmbedColor.ERROR)
                self.nominee = self.choose_chancellor()

            self.send_message(f'{self.nominee.name} has been nominated to be the Chancellor!')
            self.stage = self.next_stage()
            self.tick()

        elif self.stage == 'election':
            voting_results = self.get_voting_results()

            if voting_results:
                self.chancellor_rejections = 0
                self.chancellor = self.nominee
                self.send_message('The Chancellor was voted in!', color=EmbedColor.SUCCESS)
                if self.board['fascist'] >= 3 and self.chancellor.identity == 'Hitler':
                    message = f'Your new Chancellor {self.chancellor.name} was secretly Hitler, and with 3 or more fascist policies in place, the Fascists win!'
                    self.send_message(message, color=EmbedColor.ERROR)
                self.stage = self.next_stage()
                self.tick()
            else:
                self.chancellor_rejections += 1
                self.send_message('The Chancellor was voted down!', color=EmbedColor.WARN)
                for _ in range(3):
                    self.stage = self.next_stage()
                self.tick()

        elif self.stage == 'president':
            policies = [self.policy_deck.pop() for _ in range(3)]
            message = '<' + ', '.join([policy.card_type.title() for policy in policies]) + '> Pick 2 policies to send to the Chancellor.'
            self.send_message(message, channel=self.president.dm_channel)

            self.candidate_policies = self.pick_chosen_policies(policies)
            message = '<' + ', '.join([policy.card_type.title() for policy in self.candidate_policies]) + '> Choose a policy to enact.'
            self.send_message(message, channel=self.chancellor.dm_channel)
            self.stage = self.next_stage()
            self.tick()

        elif self.stage == 'chancellor':
            if self.board['fascist'] >= 5:
                self.send_message("The Chancellor may choose to invoke his veto power and discard both policies.")
                self.chancellor.veto = choice([True, False])
                if self.chancellor.veto:
                    self.send_message("The President must concur in order to discard both policies.")
                    self.president.veto = choice([True, False])
                    if self.president.veto:
                        self.send_message("The veto is successful, and both policies have been discarded.")
                        self.stage = self.next_stage()
                        self.tick()
                        return
                    else:
                        self.send_message("The veto fails!", color=EmbedColor.WARN)

            enacted_policy = choice(self.candidate_policies)

            self.board[enacted_policy.card_type] += 1
            self.send_message(f'A {enacted_policy.card_type} policy was passed!', color=EmbedColor.SUCCESS)

            if enacted_policy.card_type == 'fascist':
                self.do_exec_act = True
            self.stage = self.next_stage()
            self.tick()

        elif self.stage == 'summary':
            if self.chancellor_rejections == 3:
                self.chancellor_rejections = 0
                self.send_message("As three elections in a row have failed, the first policy on the top of the deck will be passed.", color=EmbedColor.WARN)

                policy = self.policy_deck.pop()
                self.board[policy.card_type] += 1
                self.send_message(f'A {policy.card_type} policy was passed!')

            if self.board['liberal'] == 5:
                self.send_message('Five liberal policies have been passed, and the Liberals win!', color=EmbedColor.SUCCESS)
                return

            if self.board['fascist'] == 6:
                self.send_message('Six fascist policies have been passed, and the Fascists win!', color=EmbedColor.ERROR)
                return

            # Redundant message, show image of board progress
            message = f'{self.board["liberal"]} liberal policies and {self.board["fascist"]} fascist policies have been passed.'
            self.send_message(message, color=EmbedColor.INFO)

            if self.policy_count < 3:
                self.generate_deck()
                self.send_message('As the deck had less than three policies remaining, the deck has been reshuffled.', color=EmbedColor.INFO)
            
            if self.do_exec_act:
                self.do_exec_act = False
                if self.executive_action() == -1:
                    return
            
            # Reset player properties - comment this out for now as we're not using it
            
            for player in self.player_list:
                player.last_chancellor = False
                player.last_president = False
                player.voted = False
                player.veto = False
            
            if self.chancellor:
                self.chancellor.last_chancellor = True
            if self.president:
                self.president.last_president = True
            print('\n' * 3)

            self.rounds += 1
            self.stage = self.next_stage()
            self.tick()
           

    def assign_identities(self):
        """Randomly assigns identities to players (Hitler, Liberal, Fascist, etc.)."""
        identities = ['Hitler']
        # Add appropriate fascists depending on player count
        identities.extend(['Fascist'] * ((self.player_count - 3) // 2))
        # Remaining identities are filled with liberals
        identities.extend(['Liberal'] * ((self.player_count - len(identities))))
        shuffle(identities)
        
        # Indicate what identity a player has and inform related parties
        fascists = []
        hitler = None
        for player, identity in zip(self.player_list, identities):
            player.identity = identity
            if identity == 'Hitler':
                hitler = player
            elif identity == 'Fascist':
                fascists.append(player)
            self.send_message(f'You are a {identity}.', channel=player.dm_channel)
        for fascist in fascists:
            team = [f.name for f in fascists if f.name != fascist.name]
            if len(team):
                team = 'The other fascists are:\n' + '\n'.join(team)
            else:
                team = 'You are the only fascist'
            message = f'{team}\n{hitler.name} is Hitler'
            self.send_message(message, channel=fascist.dm_channel)
        if len(fascists) == 1:
            message = f'{fascists[0].name} is a fascist'
            self.send_message(message, channel=hitler.dm_channel)

    def start_game(self):
        """Checks if the game can start and assigns roles to players."""
        if not 5 <= self.player_count <= 10:
            self.send_message('You must have between 5-10 players to start the game.', EmbedColor.ERROR)
            return
        self.assign_identities()

        # Runs the current stage of the game
        self.tick()

if __name__ == "__main__":
    game = SecretHitler(name='Secret Hitler')
    game.start_game()
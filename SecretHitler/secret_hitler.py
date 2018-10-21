# Base Modules
from . import bot_action, exec_action
from .cards import *
from .player import Player

# Parent Modules
import asyncio
import discord
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import Game
from utils import *

from itertools import cycle
from random import shuffle, choice, sample


class SecretHitler(Game):
    """Secret Hitler is a card game."""
    name = 'Secret Hitler'
    def __init__(self):
        super().__init__()
        
        self.player_nodes = LinkedList()
        # Keeps track of enacted policies
        self.board = {
            'fascist': 0,
            'liberal': 0
        }

        # Create an iterator that cycles every game loop (when action is valid)
        # For example, "election" can be a stage
        self.stages = cycle(['nomination', 'election', 'president', 'chancellor', 'summary'])
        self.next_stage()

        # Set starting game values
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

        self.votes = {
            'ja': [],
            'nein': []
        }
        self.rounds = 0

    @property
    def players(self):
        """Returns a list of players in the game."""
        return self.player_nodes.elements

    @property
    def vote_count(self):
        """Returns the number of players that have voted."""
        return sum(len(x) for x in self.votes.values())

    @property
    def not_voted(self):
        """Returns a list of players who have not voted."""
        return [str(player) for player in self.players if not player.voted]

    @property
    def policy_count(self):
        """Property which gives number of policy cards in the deck."""
        return len(self.policy_deck)

    @property
    def next_player(self):
        """Returns the next player in the game."""
        self.player = self.player.next
        return self.player.data

    def find_player(self, _id):
        """Finds a player by ID."""
        return self.player_nodes.find(_id, attr='id')

    async def add_player(self, discord_member: discord.Member):
        """Adds a player to the current game."""
        if discord_member:
            # DM Channels must be created for non-bot players.
            dm_channel = await discord_member.create_dm()
        else:
            dm_channel = None
        player = Player(member=discord_member, dm_channel=dm_channel)
        if discord_member is None or not self.find_player(discord_member.id):
            self.player_nodes.add(player)
            await self.send_message(f'{player.name} joined the game.')
        else:
            await self.send_message(f'{player.name} is already in the game.', color=EmbedColor.WARN)

    async def remove_player(self, player, bot=False):
        """Removes a player from the game cycle."""
        if not bot:
            node = self.find_player(player.id)
        else:
            node = self.player_nodes.find(player, attr='name')
        if not node:
            await self.send_message(f'You are not in the current game.', color=EmbedColor.ERROR)
        else:
            self.player_nodes.remove(node)
            await self.send_message(f'{node.data.name} left the game.')

    def next_stage(self):
        self.stage = next(self.stages)

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
        for player in self.players:
            if player != self.president and not player.last_chancellor and not (player.last_president and self.player_count > 5):
                valid.append(player)
        return valid

    async def executive_action(self): 
        """Manages the executive actions that the President must do after a fascist policy is passed."""

        # Executive Action - Investigate Loyalty
        if (self.board['fascist'] == 1 and self.player_count > 8) or (self.board['fascist'] == 2 and self.player_count > 6):
            await exec_action.investigate_player(self)

        # Executive Action - Policy Peek
        elif self.board['fascist'] == 3 and self.player_count < 7:
            await exec_action.policy_peek()

        # TODO: Executive Action - Special Election
        elif self.board['fascist'] == 3 and self.player_count > 7:
            await exec_action.special_election()

        # Executive Action - Execution
        elif self.board['fascist'] == 4 or self.board['fascist'] == 5:
            victim = exec_action.execution()
            if victim.identity == 'Hitler':
                await self.send_message(f'{victim.name} was executed. As he was Hitler, the Liberals win!')
                return True
            await self.send_message(f'{victim.name} was executed.')
        return False

    async def tick(self, voting_results: bool=None):
        """Handles the turn-by-turn logic of the game."""
        await asyncio.sleep(1)
        if self.stage == 'nomination':
            self.president = self.special_president if self.special_election else self.next_player
            self.special_election = False
            await self.send_message(f'{self.president.name} is the President now! They must nominate a Chancellor.')

            # Bot elects a chancellor
            if self.president.test_player:
                self.nominee = bot_action.choose_chancellor(self.valid_chancellors)
                await self.send_message(f'{self.nominee.name} has been nominated to be the Chancellor! Send in your votes!')
                self.next_stage()
                # Bot-only game, random voting results
                if self.bot_count == self.player_count:
                    await self.tick(voting_results=bot_action.vote()=='ja')

        elif self.stage == 'election':
            if voting_results:
                self.chancellor_rejections = 0
                self.chancellor = self.nominee
                await self.send_message(f'The Chancellor was voted in! The President must now send two policies to the Chancellor.', color=EmbedColor.SUCCESS)
                if self.board['fascist'] >= 3 and self.chancellor.identity == 'Hitler':
                    message = f'Your new Chancellor {self.chancellor.name} was secretly Hitler,\
                     and with 3 or more fascist policies in place, the Fascists win!'
                    await self.send_message(message, color=EmbedColor.ERROR)
                    return
                self.next_stage()
                await self.tick()
            else:
                self.chancellor_rejections += 1
                await self.send_message('The Chancellor was voted down!', color=EmbedColor.WARN)
                for _ in range(3):
                    self.next_stage()
                await self.tick()

        elif self.stage == 'president':
            self.policies = [self.policy_deck.pop() for _ in range(3)]
            message = ', '.join([policy.card_type.title() for policy in self.policies])
            # Separate the policies with spaces (e.g. `$policy fascist fascist`)
            await self.send_message(f'Choose two policies to send to the Chancellor, {self.chancellor.name}.',
                title=f'Policies: {message}', channel=self.president.dm_channel, footer=self.president.name,
                image='https://via.placeholder.com/500x250')

            # Bot chooses two policies
            if self.president.test_player:
                self.policies = bot_action.send_policies(self.policies)
                await self.send_message(f'The President has sent two policies to the Chancellor,\
                    {self.chancellor.name}, who must now choose one to enact.', color=EmbedColor.SUCCESS)
                message = ', '.join([policy.card_type.title() for policy in self.policies])
                if self.board['fascist'] >= 5:
                    await self.send_message('As there are at least 5 fascist policies enacted, the Chancellor\
                        may choose to invoke his veto power and discard both policies')
                    message += ' - Veto Allowed'
                await self.send_message('Choose a policy to enact.', title=f'Policies: {message}',
                    channel=self.chancellor.dm_channel, footer=self.chancellor.name, image='https://via.placeholder.com/500x250')
                self.next_stage()
                await self.tick()

        elif self.stage == 'chancellor':
            # Bot enacts or vetoes a policy
            if self.chancellor.test_player:
                enacted = bot_action.enact(self.policies)
                # Chancellor veto
                if self.board['fascist'] >= 5:
                    self.chancellor.veto = bot_action.veto()
                    if self.chancellor.veto:
                        await self.send_message('The Chancellor chooses to veto. The President must concur for the veto to go through.',
                            color=EmbedColor.SUCCESS)
                    else:
                        self.board[enacted.card_type] += 1
                        await self.send_message(f'A {enacted.card_type} policy was passed!', color=EmbedColor.SUCCESS)

                        if enacted.card_type == 'fascist':
                            self.do_exec_act = True
                        self.next_stage()
                        await self.tick()
                else:
                    self.board[enacted.card_type] += 1
                    await self.send_message(f'A {enacted.card_type} policy was passed!', color=EmbedColor.SUCCESS)
                    self.next_stage()
                    await self.tick()

            # President veto
            if self.president.test_player and self.chancellor.veto:
                self.president.veto = bot_action.veto()
                if self.president.veto:
                    await self.send_message('The President concurrs, and the veto is successful!', color=EmbedColor.SUCCESS)
                    self.next_stage()
                    await self.tick()
                else:
                    await self.game.send_message('The President does not concur, and the veto fails!', color=EmbedColor.WARN)
                    self.next_stage()
                    await self.game.tick()

        elif self.stage == 'summary':
            if self.chancellor_rejections == 3:
                self.chancellor_rejections = 0
                await self.send_message("As three elections in a row have failed, the first policy on the top of the deck will be passed.", color=EmbedColor.WARN)

                policy = self.policy_deck.pop()
                self.board[policy.card_type] += 1
                await self.send_message(f'A {policy.card_type} policy was passed!')

            if self.board['liberal'] == 5:
                await self.send_message('Five liberal policies have been passed, and the Liberals win!', color=EmbedColor.SUCCESS)
                self.started = False
                return

            if self.board['fascist'] == 6:
                await self.send_message('Six fascist policies have been passed, and the Fascists win!', color=EmbedColor.ERROR)
                self.started = False
                return

            # Redundant message, show image of board progress
            message = f'{self.board["liberal"]} liberal policies and {self.board["fascist"]} fascist policies have been passed.'
            await self.send_message(message, color=EmbedColor.INFO)

            if self.policy_count < 3:
                self.generate_deck()
                await self.send_message('As the deck had less than three policies remaining, the deck has been reshuffled.', color=EmbedColor.INFO)
            
            if self.do_exec_act:
                self.do_exec_act = False
                hitler_killed = await self.executive_action()
                if hitler_killed:
                    return
            
            # Reset player properties - comment this out for now as we're not using it
            for player in self.players:
                player.last_chancellor = False
                player.last_president = False
                player.voted = False
                player.veto = False

            self.votes = {
                'ja': [],
                'nein': []
            }
            
            if self.chancellor:
                self.chancellor.last_chancellor = True
            if self.president:
                self.president.last_president = True

            self.rounds += 1
            self.next_stage()
            await self.tick()
           

    async def assign_identities(self):
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
        for player, identity in zip(self.players, identities):
            player.identity = identity
            if identity == 'Hitler':
                hitler = player
            elif identity == 'Fascist':
                fascists.append(player)
            article = 'a ' if identity != 'Hitler' else ''
            await self.send_message(f'You are {article}{identity}.', channel=player.dm_channel, footer=player.name)
        for fascist in fascists:
            team = [f.name for f in fascists if f.name != fascist.name]
            if len(team):
                team = 'The other Fascists are:\n' + '\n'.join(team)
            else:
                team = 'You are the only Fascist'
            message = f'{team}\n{hitler.name} is Hitler'
            await self.send_message(message, channel=fascist.dm_channel, footer=fascist.name)
        if len(fascists) == 1:
            message = f'{fascists[0].name} is a Fascist'
            await self.send_message(message, channel=hitler.dm_channel, footer=hitler.name)

    async def start_game(self):
        """Checks if the game can start and assigns roles to players."""
        if not 5 <= self.player_count <= 10:
            await self.send_message('You must have between 5-10 players to start the game.', color=EmbedColor.ERROR)
            return
        await self.assign_identities()

        # The first player is the first to join
        self.player = self.player_nodes.head
        # Runs the current stage of the game
        self.started = True
        await self.tick()

if __name__ == "__main__":
    game = SecretHitler(name='Secret Hitler')
    game.start_game()
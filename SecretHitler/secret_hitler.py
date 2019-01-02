# Base Modules
from . import bot_action, exec_action, stages
from .cards import *
from .player import Player

# Parent Modules
import asyncio
import discord
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import Game
from utils import *

from itertools import cycle, islice
from random import shuffle, choice, sample, randint


class SecretHitler(Game):
    """Secret Hitler is a card game."""
    name = 'Secret Hitler'
    def __init__(self, bot):
        super().__init__(bot)

        self.load_message = """\
Secret Hitler is a dramatic game of political intrigue and betrayal set in 1930's Germany. \
Players are secretly divided into two teams - liberals and fascists. \
Known only to each other, the fascists coordinate to sow distrust and install their cold-blooded leader. \
The liberals must find and stop the Secret Hitler before it is too late.
"""
        self.asset_folder = 'SecretHitler/assets/'
        # self.load_image = image_merge('_secret.png', '_hitler.png', asset_folder=self.asset_folder)
        self.load_image = 'title.png'
        
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
        self.nominee = None
        self.candidate_policies = None
        self.enact_msg = None
        self.special_election = False
        self.do_exec_act = False
        self.hitler_dead = False
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
        return [str(player) for player in self.players if not player.voted and not player.bot]

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
        node = self.player_nodes.find(_id, attr='id')
        return node.data if node else None

    async def add_player(self, member: discord.Member):
        """Adds a player to the current game."""
        if not member.bot:
            # DM Channels must be created for non-bot players.
            await member.create_dm()
        player = Player(member=member)
        if not self.find_player(member.id):
            self.player_nodes.add(player)
            if player.bot:
                self.bots[player.name] = player.id
            else:
                await self.send_message(f'{player.name} joined the game.')
        elif not player.bot:
            await self.send_message(f'{player.name} is already in the game.', color=EmbedColor.WARN)

    async def remove_player(self, player_id):
        """Removes a player from the game cycle."""
        node = self.player_nodes.find(player_id, attr='id')
        if not node:
            await self.send_message(f'That player is not in the current game.', color=EmbedColor.ERROR)
        else:
            self.player_nodes.remove(node)
            await self.send_message(f'{node.data.name} left the game.')

    def next_stage(self, skip=1):
        self.stage = next(islice(self.stages, skip - 1, skip))

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
        if (self.board['fascist'] == 1 and self.player_count >= 9) or (self.board['fascist'] == 2 and self.player_count >= 7):
            self.stage = 'investigate_loyalty'
            await self.send_message("The President must now investigate another player's loyalty!")
            if self.president.bot:
                suspect = await exec_action.investigate_loyalty(self)
                self.previously_investigated.append(suspect)
                identity = suspect.identity if suspect.identity != 'Hitler' else 'Fascist'
                image = f'party_{identity.lower()}.png'
                await self.send_message(f'{suspect.name} is a {identity}.', channel=self.president.dm_channel, footer=self.president.name, image=image)
                await self.reset_rounds()
                
        # Executive Action - Policy Peek
        elif self.board['fascist'] == 3 and self.player_count <= 6:
            self.stage = 'policy_peek'
            await exec_action.policy_peek(self)
            policy_names = [policy.card_type.title() for policy in self.policy_deck[-3:]]
            message = ', '.join(policy_names)
            image = image_merge(*[f'{p.lower()}_policy.png' for p in policy_names], asset_folder=self.asset_folder, pad=True)
            await self.send_message('', title=f'Top 3 Policies: {message}',
                channel=self.president.dm_channel, footer=self.president.name if self.president.bot else '', image=image)
            await self.reset_rounds()

        # Executive Action - Special Election
        elif self.board['fascist'] == 3 and self.player_count >= 7:
            self.stage = 'special_election'
            await self.send_message('The President must appoint another player to be President!')
            if self.president.bot:
                new_president = await exec_action.special_election(self)
                self.president = new_president
                self.special_election = True
                await self.send_message(f'{new_president.name} was chosen to be President.')
                await self.reset_rounds()

        # Executive Action - Execution
        elif self.board['fascist'] == 4 or self.board['fascist'] == 5:
            print(f'Before execution stage set {self.stage}')
            self.stage = 'execution'
            print(f'Before execution message {self.stage}')
            await self.send_message('The President must now execute a player!')
            print(f'After execution message {self.stage}')
            if self.president.bot:
                victim = await exec_action.execution(self)
                if victim.identity == 'Hitler':
                    await self.send_message(f'{victim.name} was executed. As he was Hitler, the Liberals win!')
                    self.hitler_dead = True
                    self.started = False
                    return
                else:
                    await self.send_message(f':knife: {victim.name} was executed.')
                    await self.reset_rounds()

        # Executive action does not apply
        else:
            await self.reset_rounds()

    async def tick(self, voting_results: bool=None):
        """Handles the turn-by-turn logic of the game."""
        print(f'Ticking at {self.stage}')
        await asyncio.sleep(1)
        await stages.tick(self, voting_results)

    async def reset_rounds(self):
        """Resets the round after displaying the summary."""
        if self.hitler_dead:
            return

        for player in self.players:
            player.last_chancellor = False
            if not self.special_election:
                player.last_president = False
            player.voted = False
            player.veto = False

        self.votes = {
            'ja': [],
            'nein': []
        }
        
        if self.chancellor:
            self.chancellor.last_chancellor = True
        if self.president and not self.special_election:
            self.president.last_president = True

        self.rounds += 1
        self.next_stage()
        await self.tick()

    async def assign_identities(self):
        """Randomly assigns identities to players (Hitler, Liberal, Fascist, etc.)."""
        # Since this takes a long time, show that a process is occurring
        async with self.channel.typing():
            identities = ['Hitler']
            # Add appropriate fascists depending on player count
            identities.extend(['Fascist'] * ((self.player_count - 3) // 2))
            # Remaining identities are filled with liberals
            identities.extend(['Liberal'] * ((self.player_count - len(identities))))
            shuffle(identities)
            
            # Indicate what identity a player has and inform related parties
            fascists = []
            hitler = None
            counts = {
                'Hitler': 0,
                'Liberal': 0,
                'Fascist': 0
            }
            for player, identity in zip(self.players, identities):
                player.identity = identity
                if identity == 'Hitler':
                    hitler = player
                elif identity == 'Fascist':
                    fascists.append(player)
                player.image = f'{identity.lower()}_{counts[identity]}.png'
                counts[identity] += 1
            for player in self.players:
                article = 'a ' if player.identity != 'Hitler' else ''
                message = f'You are {article}{player.identity}.'
                if player.identity == 'Fascist':
                    team = [f.name for f in fascists if f.name != player.name]
                    if len(team):
                        message = 'You are a Fascist along with:\n' + '\n'.join(team)
                    else:
                        message = 'You are the only Fascist.'
                elif player.identity == 'Hitler' and len(fascists) == 1:
                    message = f'You are Hitler.\n{fascists[0].name} is a Fascist.'
                await self.send_message(message, channel=player.dm_channel, footer=player.name if player.bot else '', image=player.image)

    async def on_load(self):
        """Creates the interface to join/leave the game."""
        await self.send_message(title=self.name, description=self.load_message, image=self.load_image, color=EmbedColor.SUCCESS)
        gui_embed = discord.Embed(title='Players', description='...', color=EmbedColor.SUCCESS)
        gui_embed.set_footer(text='Join using the buttons below!')

        gui = await self.channel.send(embed=gui_embed)
        await gui.add_reaction(self.emojis['add_user'])
        await gui.add_reaction(self.emojis['remove_user'])
        await gui.add_reaction(self.emojis['bot'])
        await gui.add_reaction(self.emojis['add'])
        await gui.add_reaction(self.emojis['remove'])
        await gui.add_reaction(self.emojis['01'])

        bot_add = 1
        check_user = lambda r, u: r.message.id == gui.id and u.has_role('Tabletop Master')
        while True:
            reaction, user = await self.bot.wait_for('reaction_add', check=check_user)
            await self.channel.send(f'You ({user}) reacted with: {reaction} {reaction.emoji}')
            break

    async def start_game(self):
        """Checks if the game can start and assigns roles to players."""
        # Custom Emojis
        self.emojis['ja'] = discord.utils.get(self.channel.guild.emojis, name='ja')
        self.emojis['nein'] = discord.utils.get(self.channel.guild.emojis, name='nein')
        self.emojis['veto'] = '📝'
        self.emojis['yes'] = '✅'
        self.emojis['no'] = '❌'

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
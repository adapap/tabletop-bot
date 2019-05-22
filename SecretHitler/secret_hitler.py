# Local
from . import bot_action, exec_action, stages
from .cards import *
from .player import Player

# External
import asyncio
import discord
from itertools import count, cycle, islice
import io
from PIL import Image
from random import shuffle, choice, sample, randint
import re
import os, sys

# Parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import Game
from image import ImageUtil
from utils import *
import utils


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
        self.load_image = 'title.png'
        
        self.player_nodes = LinkedList()
        # Keeps track of enacted policies
        self.board = {
            'fascist': 0,
            'liberal': 0
        }

        # Create an iterator that cycles every game loop (when action is valid)
        # For example, "election" can be a stage
        self.stage = None
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

    def render_board(self):
        """Returns the image data for the current board progress."""
        liberal_board = Image.open(f'{self.asset_folder}liberal_board.png').convert('RGBA')
        players = self.player_count
        if players <= 6:
            fascist_board = Image.open(f'{self.asset_folder}fascist_board_56.png').convert('RGBA')
        elif players <= 8:
            fascist_board = Image.open(f'{self.asset_folder}fascist_board_78.png').convert('RGBA')
        elif players <= 10:
            fascist_board = Image.open(f'{self.asset_folder}fascist_board_910.png').convert('RGBA')

        liberal_policy = Image.open(f'{self.asset_folder}liberal_policy.png').convert('RGBA')
        fascist_policy = Image.open(f'{self.asset_folder}fascist_policy.png').convert('RGBA')
        w, h = liberal_policy.size
        ratio = 112 / h
        size = (int(w * ratio), int(h * ratio))

        liberal_policy.thumbnail(size, Image.ANTIALIAS)
        fascist_policy.thumbnail(size, Image.ANTIALIAS)

        election_tracker = Image.open(f'{self.asset_folder}election_tracker.png').convert('RGBA')
        w, h = election_tracker.size
        ratio = 26 / h
        size = (int(w * ratio), int(h * ratio))

        election_tracker.thumbnail(size, Image.ANTIALIAS)

        # Liberal Policy
        left = 95
        top = 54
        offset = 95
        for i in range(self.board['liberal']):
            pos = (left + offset * i, top)
            liberal_board.alpha_composite(liberal_policy, pos)
        
        # Fascist Policy
        left = 51
        offset = 93
        for i in range(self.board['fascist']):
            pos = (left + offset * i, top)
            fascist_board.alpha_composite(fascist_policy, pos)

        # Election Tracker
        left = 212
        top = 182
        offset = 63.5
        for i in range(self.chancellor_rejections):
            pos = (round(left + offset * i), top)
            liberal_board.alpha_composite(election_tracker, pos)

        liberal = io.BytesIO()
        liberal_board.save(liberal, format='PNG')
        liberal = liberal.getvalue()
        fascist = io.BytesIO()
        fascist_board.save(fascist, format='PNG')
        fascist = fascist.getvalue()

        board = ImageUtil.merge(liberal, fascist, axis=1)
        return board

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
                pass # Joining using buttons renders this irrelevant
                # await self.message(f'{player.name} joined the game.')
        elif not player.bot:
            await self.warn(f'{player.name} is already in the game.')

    async def remove_player(self, player_id):
        """Removes a player from the game cycle."""
        node = self.player_nodes.find(player_id, attr='id')
        if not node:
            await self.error(f'That player is not in the current game.')
        else:
            self.player_nodes.remove(node)
            pass # Leaving using buttons renders this irrelevant
            # await self.message(f'{node.data.name} left the game.')

    def next_stage(self, skip=1):
        """Skips `skip` stages in the stage cycle."""
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
            await self.message("The President must now investigate another player's loyalty!")
            if self.president.bot:
                suspect = await exec_action.investigate_loyalty(self)
                self.previously_investigated.append(suspect)
                identity = suspect.identity if suspect.identity != 'Hitler' else 'Fascist'
                image = f'party_{identity.lower()}.png'
                await self.message(f'{suspect.name} is a {identity}.', channel=self.president.dm_channel, footer=self.president.name, image=image)
                await self.reset_rounds()
                
        # Executive Action - Policy Peek
        elif self.board['fascist'] == 3 and self.player_count <= 6:
            self.stage = 'policy_peek'
            await exec_action.policy_peek(self)
            policy_names = [policy.card_type.title() for policy in self.policy_deck[-3:]]
            message = ', '.join(policy_names)
            image = ImageUtil.merge(*map(ImageUtil.from_file, [f'{self.asset_folder}{p.lower()}_policy.png' for p in policy_names]), pad=True)
            await self.message('', title=f'Top 3 Policies: {message}',
                channel=self.president.dm_channel, footer=self.president.name if self.president.bot else '', image=image)
            await self.reset_rounds()

        # Executive Action - Special Election
        elif self.board['fascist'] == 3 and self.player_count >= 7:
            self.stage = 'special_election'
            await self.message('The President must appoint another player to be President!')
            if self.president.bot:
                new_president = await exec_action.special_election(self)
                self.president = new_president
                self.special_election = True
                await self.message(f'{new_president.name} was chosen to be President.')
                await self.reset_rounds()

        # Executive Action - Execution
        elif self.board['fascist'] == 4 or self.board['fascist'] == 5:
            self.stage = 'execution'
            await self.message('The President must now execute a player!')
            if self.president.bot:
                victim = await exec_action.execution(self)
                if victim.identity == 'Hitler':
                    await self.message(f'{victim.name} was executed. As he was Hitler, the Liberals win!')
                    self.hitler_dead = True
                    self.started = False
                    return
                else:
                    await self.message(f':knife: {victim.name} was executed.')
                    await self.reset_rounds()

        # Executive action does not apply
        else:
            await self.reset_rounds()

    async def tick(self, voting_results: bool=None):
        """Handles the turn-by-turn logic of the game."""
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
                await self.message(message, channel=player.dm_channel, footer=player.name if player.bot else '', image=player.image)

    async def on_load(self):
        """Creates the interface to join/leave the game."""
        await self.success(title=self.name, description=self.load_message, image=self.load_image)
        gui_embed = discord.Embed(title='Players', description='...')
        gui_embed.set_footer(text='Join using the buttons below!')

        gui = await self.channel.send(embed=gui_embed)
        await gui.add_reaction(self.emojis['add_user'])
        await gui.add_reaction(self.emojis['remove_user'])
        await gui.add_reaction(self.emojis['bot'])
        await gui.add_reaction(self.emojis['play'])

        bot_add = 1
        react_check = lambda r, u: r.message.id == gui.id and not u.bot
        while True:
            reaction, user = await self.bot.wait_for('reaction_add', check=react_check)
            await gui.remove_reaction(reaction, user)
            command = reaction.emoji.name
            if command == 'play':
                if not 5 <= self.player_count <= 10:
                    await self.error('You must have between 5-10 players to start the game.')
                else:
                    await self.start_game()
                    break
            elif command == 'add_user':
                await self.add_player(user)
                gui_embed.description = '\n'.join(player.name for player in self.players)
                await gui.edit(embed=gui_embed)
            elif command == 'remove_user':
                await self.remove_player(user.id)
                gui_embed.description = '\n'.join(player.name for player in self.players) if self.player_count else '...'
                await gui.edit(embed=gui_embed)
            elif command == 'bot' and user.has_role('Tabletop Master'):
                bot_check = lambda m: m.author.id == user.id
                prompt = await self.message('How many bots?')
                msg = await self.bot.wait_for('message', check=bot_check)
                await asyncio.sleep(1)
                await prompt.delete()
                await msg.delete()
                try:
                    num_bots = int(msg.content)
                    if num_bots < 1:
                        for _ in range(abs(num_bots)):
                            if len(self.bots) == 0:
                                continue
                            bot_id = self.bots.pop(list(self.bots)[-1])
                            await self.remove_player(bot_id)
                    for _ in range(num_bots):
                        member = discord.Object(id=str(next(self.uid_gen)))
                        member.display_name = f'Bot{next(self.nametag_gen)}'
                        member.dm_channel = None
                        member.bot = True
                        await self.add_player(member)
                    bots = ', '.join(name for name in self.bots)
                    # Unnecessary message?
                    # await self.message(f'{num_bots} bot{"s" if num_bots > 1 else ""} ({bots}) joined the game.')
                    gui_embed.description = '\n'.join(player.name for player in self.players)
                    await gui.edit(embed=gui_embed)
                except ValueError:
                    await self.error('Invalid number.')

    async def start_game(self):
        """Checks if the game can start and assigns roles to players."""
        # Custom Emojis
        self.emojis['ja'] = discord.utils.get(self.channel.guild.emojis, name='ja')
        self.emojis['nein'] = discord.utils.get(self.channel.guild.emojis, name='nein')
        self.emojis['veto'] = '📝'
        self.emojis['yes'] = '✅'
        self.emojis['no'] = '❌'

        await self.assign_identities()

        # The first player is the first to join
        self.player = self.player_nodes.head
        # Runs the current stage of the game
        self.started = True
        await self.tick()

if __name__ == "__main__":
    game = SecretHitler(name='Secret Hitler')
    game.start_game()
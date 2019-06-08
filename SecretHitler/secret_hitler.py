import asyncio
import discord
import io
import re
import os
import sys
import time
from discord import Embed
from itertools import count, cycle, islice
from PIL import Image
from random import shuffle, choice, sample, randint

from . import bot_action
from .cards import PolicyCard
from .player import Player

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Card import Deck
from Game import Game
from Image import ImageUtil
from Player import PlayerCycle
from Utils import EmbedColor


class SecretHitler(Game):
    """Secret Hitler is a card game."""
    name = 'Secret Hitler'
    load_message = """\
Secret Hitler is a dramatic game of political intrigue and betrayal set in 1930's Germany. \
Players are secretly divided into two teams - liberals and fascists. \
Known only to each other, the fascists coordinate to sow distrust and install their cold-blooded leader. \
The liberals must find and stop the Secret Hitler before it is too late.
"""
    load_image = 'title.png'

    def __init__(self, bot):
        super().__init__(bot, __file__)
        self.player_cycle = PlayerCycle(Player)
        # Keeps track of enacted policies
        self.board = {
            'fascist': 0,
            'liberal': 0
        }

        # Set starting game values
        self.chancellor_rejections = 0
        self.chancellor = None
        self.president = None
        self.nominee = None
        self.candidate_policies = None
        self.nominate_msg = None
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
        return self.player_cycle.players()

    @property
    def real_players(self):
        """Returns a list of players that are not bots."""
        return self.player_cycle.players(filter_=lambda p: not p.bot)

    @property
    def bots(self):
        """Returns a list of bots in the game."""
        return self.player_cycle.bots()

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
        return self.player

    @property  
    def valid_chancellors(self):
        """Returns a list of valid chancellor nominees."""
        valid = []
        for player in self.players:
            if player != self.president and not player.last_chancellor and not (player.last_president and self.player_count > 5):
                valid.append(player)
        return valid

    def policy_type_count(self, type_):
        """Counts how many policies of a type are remaining in the deck."""
        return self.policy_deck.count_of(card_type=type_)

    def render_board(self):
        """Returns the image data for the current board progress."""
        liberal_board = Image.open(self.get_asset('liberal_board.png')).convert('RGBA')
        players = self.player_count
        if players <= 6:
            fascist_board = Image.open(self.get_asset('fascist_board_56.png')).convert('RGBA')
        elif players <= 8:
            fascist_board = Image.open(self.get_asset('fascist_board_78.png')).convert('RGBA')
        elif players <= 10:
            fascist_board = Image.open(self.get_asset('fascist_board_910.png')).convert('RGBA')

        liberal_policy = Image.open(self.get_asset('liberal_policy.png')).convert('RGBA')
        fascist_policy = Image.open(self.get_asset('fascist_policy.png')).convert('RGBA')
        ImageUtil.scale(liberal_policy, w=112)
        ImageUtil.scale(fascist_policy, w=112)

        election_tracker = Image.open(self.get_asset('election_tracker.png')).convert('RGBA')
        ImageUtil.scale(election_tracker, w=26)

        # Liberal Policy
        left, top, offset = 95, 54, 95
        for i in range(self.board['liberal']):
            pos = (left + offset * i, top)
            liberal_board.alpha_composite(liberal_policy, pos)
        
        # Fascist Policy
        left, offset = 51, 93
        for i in range(self.board['fascist']):
            pos = (left + offset * i, top)
            fascist_board.alpha_composite(fascist_policy, pos)

        # Election Tracker
        left, top, offset = 212, 182, 63.5
        pos = (round(left + offset * (self.chancellor_rejections)), top)
        liberal_board.alpha_composite(election_tracker, pos)

        liberal = io.BytesIO()
        liberal_board.save(liberal, format='PNG')
        liberal = liberal.getvalue()
        fascist = io.BytesIO()
        fascist_board.save(fascist, format='PNG')
        fascist = fascist.getvalue()

        board = ImageUtil.merge(liberal, fascist, axis=1)
        return board

    def generate_deck(self):
        """Generates a deck of policy cards."""
        # There are 6 fascist policies and 11 liberal policies in a deck
        # If the deck is emptied, reshuffle the deck without the board cards
        self.policy_deck = Deck()
        self.policy_deck.insert(card=PolicyCard(card_type='fascist', image='fascist_policy.png'), count=(11 - self.board['fascist']))
        self.policy_deck.insert(card=PolicyCard(card_type='liberal', image='liberal_policy.png'), count=(6 - self.board['liberal']))
        self.policy_deck.shuffle()

    def react_select(self, msg_id, user_id):
        def predicate(reaction, user):
            return reaction.message.id == msg_id and user.id == user_id
        return predicate

    async def executive_action(self): 
        """Manages the executive actions that the President must do after a fascist policy is passed."""

        # Executive Action - Investigate Loyalty
        if (self.board['fascist'] == 1 and self.player_count >= 9) or (self.board['fascist'] == 2 and self.player_count >= 7):
            self.stage = 'investigate_loyalty'
            await self.message("The President must now investigate another player's loyalty!")
            if self.president.bot:
                suspect = bot_action.investigate_loyalty(game=self)
                self.previously_investigated.append(suspect)
                identity = suspect.identity if suspect.identity != 'Hitler' else 'Fascist'
                image = self.get_asset(f'party_{identity.lower()}.png')
                await self.message(f'{suspect.name} is a {identity}.', channel=self.president.dm_channel, footer=self.president.name, image=image)
                
        # Executive Action - Policy Peek
        elif self.board['fascist'] == 3 and self.player_count <= 6:
            self.stage = 'policy_peek'
            await self.message('The President will now peek at the top three policies in the deck!')
            policy_names = map(lambda p: p.name, self.policy_deck[-3:])
            message = ', '.join(policy_names)
            image = ImageUtil.merge(*map(ImageUtil.from_file, [self.get_asset(p.image) for p in self.policy_deck[-3:]]), pad=True)
            await self.message('', title=f'Top 3 Policies: {message}',
                channel=self.president.dm_channel, footer=self.president.name if self.president.bot else '', image=image)

        # Executive Action - Special Election
        elif self.board['fascist'] == 3 and self.player_count >= 7:
            self.stage = 'special_election'
            await self.message('The President must appoint another player to be President!')
            if self.president.bot:
                new_president = bot_action.special_election(game=self)
                self.president = new_president
                self.special_election = True
                await self.message(f'{new_president.name} was chosen to be President.')

        # Executive Action - Execution
        elif self.board['fascist'] == 4 or self.board['fascist'] == 5:
            self.stage = 'execution'
            await self.message('The President must now execute a player!')
            if self.president.bot:
                victim = bot_action.execution(game=self)
                if victim.identity == 'Hitler':
                    await self.message(f'{victim.name} was executed. As he was Hitler, the Liberals win!')
                    self.hitler_dead = True
                    await self.end_game()
                else:
                    await self.message(f':knife: {victim.name} was executed.')

    async def vote_callback(self):
        if len(self.not_voted) == 0:
            if self.bot_count > 0:
                # Bots send in votes
                for bot in self.bots:
                    vote = bot_action.vote()
                    bot.voted = True
                    self.votes[vote].append(bot)
            vote_ja = '\n'.join([player.name for player in self.votes['ja']])
            vote_nein = '\n'.join([player.name for player in self.votes['nein']])
            if vote_ja == '':
                vote_ja = 'None!'
            if vote_nein == '':
                vote_nein = 'None!'
            fields = [{'name': 'Ja', 'value': vote_ja, 'inline': True}, {'name': 'Nein', 'value': vote_nein, 'inline': True}]
            await self.message('', title=f'Election of {self.nominee.name} as Chancellor - Voting Results', fields=fields)
            nominated = len(self.votes['ja']) > len(self.votes['nein'])
            await self.election(nominated=nominated)

    async def nomination(self):
        """The nomination stage involves the President nominating a Chancellor for election."""
        if not self.special_election:
            self.president = self.next_player
        else:
            self.special_election = False
        fields = [{
            'name': 'Valid Nominees',
            'value': '\n'.join(f'{i + 1}: {x}' for i, x in enumerate(self.valid_chancellors))
        }]
        self.nominate_msg = await self.message(f'{self.president.name} is the President now!\nThey must nominate a Chancellor.', fields=fields)

        # Bot elects a chancellor
        if self.president.bot:
            self.nominee = bot_action.choose_chancellor(self.valid_chancellors)
            await self.message(f'{self.nominee.name} has been nominated to be the Chancellor! Send in your votes!')
            vote_msg = await self.message(title=f'0/{len(self.not_voted)} players voted.')
            
            async def vote_handler(msg, player):
                vote, _ = await self.bot.wait_for('reaction_add', check=self.react_select(msg.id, player.id))
                vote = vote.emoji.name
                player.voted = True
                self.votes[vote].append(player)
                not_voted_msg = f'Waiting for: {", ".join(self.not_voted)}' if 0 < len(self.not_voted) <= 3 else ''
                await vote_msg.edit(embed=Embed(
                    title=f'{self.vote_count}/{self.vote_count + len(self.not_voted)} players voted.',
                    description=not_voted_msg,
                    color=EmbedColor.INFO))
                await self.vote_callback()

            vote_coros = []
            for player in self.real_players:
                image = ImageUtil.merge(*map(ImageUtil.from_file, map(self.get_asset, ['vote_ja.png', 'vote_nein.png'])), pad=True)
                msg = await self.message(description=f'Vote for election of {self.nominee.name} as Chancellor',
                    image=image, channel=player.dm_channel)
                await msg.add_reaction(self.emojis['ja'])
                await msg.add_reaction(self.emojis['nein'])
                handler = vote_handler(msg, player)
                vote_coros.append(handler)
            await asyncio.gather(*vote_coros)
        else: # President is not a bot
            select_emojis = [self.emojis[str(i).zfill(2)] for i in range(1, len(self.valid_chancellors) + 1)]
            msg = self.nominate_msg
            for emoji in select_emojis:
                await msg.add_reaction(emoji)
            reaction, _ = await self.bot.wait_for('reaction_add', check=self.react_select(msg.id, self.president.id))
            index = select_emojis.index(reaction.emoji)
            self.nominee = self.valid_chancellors[index]
            await self.message(f'{self.nominee.name} has been nominated to be the Chancellor! Send in your votes!')
            vote_msg = await self.message(title=f'0/{len(self.not_voted)} players voted.')
                
            async def vote_handler(msg, player):
                vote, _ = await self.bot.wait_for('reaction_add', check=self.react_select(msg.id, player.id))
                vote = vote.emoji.name
                player.voted = True
                self.votes[vote].append(player)
                not_voted_msg = f'Waiting for: {", ".join(self.not_voted)}' if 0 < len(self.not_voted) <= 3 else ''
                await vote_msg.edit(embed=Embed(
                    title=f'{self.vote_count}/{self.player_count - self.bot_count} players voted.',
                    description=not_voted_msg,
                    color=EmbedColor.INFO))
                await self.vote_callback(self)

            vote_coros = []
            for player in self.real_players:
                image = ImageUtil.merge(*map(ImageUtil.from_file, map(self.get_asset, ['vote_ja.png', 'vote_nein.png'])), pad=True)
                msg = await self.message(description=f'Vote for election of {self.nominee.name} as Chancellor',
                    image=image, channel=player.dm_channel)
                await msg.add_reaction(self.emojis['ja'])
                await msg.add_reaction(self.emojis['nein'])
                handler = vote_handler(msg, player)
                vote_coros.append(handler)
            await asyncio.gather(*vote_coros)
        # Bot-only game, random voting results
        if all(player.bot for player in self.players):
            await self.election(nominated=choice([True, False]))

    async def election(self, nominated: bool):
        """
        Election involves all players voting for the election of the nominated Chancellor.
        The param `nominated` tells whether or not the nomination succeeded (majority voted 'Ja').
        """
        if nominated:
            self.chancellor_rejections = 0
            self.chancellor = self.nominee
            await self.success(f'The Chancellor was voted in! The President, {self.president.name}, must now send two policies to the Chancellor.')
            if self.board['fascist'] >= 3 and self.chancellor.identity == 'Hitler':
                message = f'Your new Chancellor {self.chancellor.name} was secretly Hitler, and with 3 or more fascist policies in place, the Fascists win!'
                await self.error(message)
                return await self.end_game()
            await self.select_policies()
        else:
            self.chancellor_rejections += 1
            await self.warn('The Chancellor was voted down!')
            await self.summary()

    async def select_policies(self):
        """The President must choose two policies to send to the Chancellor."""
        self.policies = self.policy_deck.top(3)
        message = ', '.join(map(lambda p: p.name, self.policies))
        image = ImageUtil.merge(*map(ImageUtil.from_file, map(lambda p: self.get_asset(p.image), self.policies)), pad=True)
        msg = await self.message(f'Choose two policies to send to the Chancellor, {self.chancellor.name}.',
            title=f'Policies: {message}', channel=self.president.dm_channel, footer=self.president.name if self.president.bot else '',
            image=image)
        if not self.president.bot:
            select_emojis = [self.emojis[str(i).zfill(2)] for i in range(1, 4)]
            for emoji in select_emojis:
                await msg.add_reaction(emoji)
            chancellor_policies = []
            while len(chancellor_policies) < 2:
                reaction, _ = await self.bot.wait_for('reaction_add', check=self.react_select(msg.id, self.president.id))
                policy_index = select_emojis.index(reaction.emoji)
                if policy_index not in chancellor_policies:
                    chancellor_policies.append(policy_index)
            self.policies = [self.policies[i] for i in sorted(chancellor_policies)]
        else: # Bot chooses two policies
            self.policies = bot_action.select_policies(self.policies)
        
        await self.success(f'The President has sent two policies to the Chancellor, {self.chancellor.name}, who must now choose one to enact.')
        if self.board['fascist'] >= 5:
            await self.message('As there are at least 5 fascist policies enacted, the Chancellor may choose to invoke his veto power and discard both policies.')
            message += ' - Veto Allowed'
        
        self.enact_msg = await self.message('Choose a policy to enact.', title=f'Policies: {message}',
            channel=self.chancellor.dm_channel, footer=self.chancellor.name if self.chancellor.bot else '', image=image)
        await self.enact_policy()

    async def enact_policy(self):
        """The Chancellor enacts a policy, or vetoes if able and willing."""
        veto_msg = None
        # Bot enacts or vetoes a policy
        if self.chancellor.bot:
            enacted = bot_action.enact_policy(self.policies)
            # Chancellor veto
            if self.board['fascist'] >= 5:
                self.chancellor.veto = bot_action.veto()
            if not self.chancellor.veto:
                self.board[enacted.card_type] += 1
                if enacted.card_type == 'fascist':
                    self.do_exec_act = True
                await self.success(f'A {enacted.card_type} policy was passed!')

        # Human reacts for enact / veto
        else:
            select_emojis = [self.emojis[str(i).zfill(2)] for i in range(1, 3)]
            if self.board['fascist'] >= 5:
                select_emojis.extend([self.emojis['veto']])
            msg = self.enact_msg
            for emoji in select_emojis:
                await msg.add_reaction(emoji)
            reaction, _ = await self.bot.wait_for('reaction_add', check=self.react_select(msg.id, self.chancellor.id))
            index = select_emojis.index(reaction.emoji)
            if index < 2:
                # Enact a policy if number is chosen
                enacted = self.policies[index]
                self.board[enacted.card_type] += 1
                if enacted.card_type == 'fascist':
                    self.do_exec_act = True
                await self.success(f'A {enacted.card_type} policy was passed!')
            else:
                # Otherwise, veto emoji is chosen
                self.chancellor.veto = True
                await self.veto()
        await self.summary()

    async def veto(self):
        """If the Chancellor initiates a veto, the President must concur to discard the policy."""
        if self.chancellor.veto:
            veto_msg = await self.message('The Chancellor chooses to veto. The President must concur for the veto to go through.')
            if not self.president.bot:
                select_emojis = [self.emojis['yes'], self.emojis['no']]
                for emoji in select_emojis:
                    await veto_msg.add_reaction(emoji)
                reaction, _ = await self.bot.wait_for('reaction_add', check=self.react_select(veto_msg.id, self.president.id))
                index = select_emojis.index(reaction.emoji)
                self.president.veto = bool(index - 1)
            else:
                self.president.veto = bot_action.veto()

            if self.president.veto:
                await self.success('The President concurrs, and the veto is successful!')
            else:
                await self.self.warn('The President does not concur, and the veto fails!')
                select_emojis = [self.emojis[str(i).zfill(2)] for i in range(1, 3)]
                msg = self.enact_msg
                for emoji in select_emojis:
                    await msg.add_reaction(emoji)
                reaction, _ = await self.bot.wait_for('reaction_add', check=self.react_select(msg.id, self.chancellor.id))
                index = select_emojis.index(reaction.emoji)
                # Enact a policy if number is chosen
                enacted = self.policies[index]
                self.board[enacted.card_type] += 1
                if enacted.card_type == 'fascist':
                    self.do_exec_act = True
                await self.success(f'A {enacted.card_type} policy was passed!')

    async def summary(self):
        """Handles Chancellor rejections, win conditions, and loops back to nomination."""
        if self.chancellor_rejections == 3:
            self.chancellor_rejections = 0
            await self.warn("As three elections in a row have failed, the first policy on the top of the deck will be passed.")

            policy = self.policy_deck.pop()
            self.board[policy.card_type] += 1
            await self.message(f'A {policy.card_type} policy was passed!')

        if self.board['liberal'] == 5:
            await self.success('Five liberal policies have been passed, and the Liberals win!')
            return await self.end_game()

        if self.board['fascist'] == 6:
            await self.error('Six fascist policies have been passed, and the Fascists win!')
            return await self.end_game()

        image = self.render_board()
        await self.message(title=f"Policies remaining in deck: {self.policy_count}",
            color=EmbedColor.INFO, image=image, footer='Order: ' + ' → '.join([x.name for x in self.players]) + ' ↺')

        if self.policy_count < 3:
            self.generate_deck()
            # Should there be a message saying the deck was reshuffled?
            # await self.message('As the deck had less than three policies remaining, the deck has been reshuffled.', color=EmbedColor.INFO)
        
        if self.do_exec_act:
            self.do_exec_act = False
            await self.executive_action()
        
        # Reset player statuses
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
        await self.nomination()

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
                player.image = self.get_asset(f'{identity.lower()}_{counts[identity]}.png')
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
                    message += f'\n{hitler.name} is Hitler.'
                elif player.identity == 'Hitler' and len(fascists) == 1:
                    message = f'You are Hitler.\n{fascists[0].name} is a Fascist.'
                await self.message(message, channel=player.dm_channel, footer=player.name if player.bot else '', image=player.image)

    async def on_load(self):
        """Creates the interface to join/leave the game."""
        await super().on_load()
        await self.player_join_gui(players=self.player_cycle)

    async def start_game(self):
        """Checks if the game can start and assigns roles to players."""
        await super().start_game()
        self.emojis.update({
            'veto': '📝',
            'yes': '✅',
            'no': '❌'
        })

        await self.assign_identities()
        # Pick a random starting player
        self.player = self.player_cycle.random_player()
        # Runs the current stage of the game
        self.started = True
        await self.nomination()

    async def end_game(self):
        """Runs after the game end conditions are met."""
        self.started = False
        duration = time.strftime('%H:%M:%S', time.gmtime(self.duration))
        await self.message('The game has ended. You may now delete this channel, or it will be deleted when you load another game.',
            footer=f'Time Elapsed: {duration}')
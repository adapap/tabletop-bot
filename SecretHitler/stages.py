import asyncio
import discord
from discord import Embed

from . import bot_action
from utils import *
import utils

def react_select(msg_id, user_id):
    def predicate(reaction, user):
        return reaction.message.id == msg_id and user.id == user_id
    return predicate

async def vote_callback(game):
    if len(game.not_voted) == 0:
        if game.bot_count > 0:
            # Bots send in votes
            for bot_id in game.bots.values():
                bot = game.find_player(bot_id)
                vote = bot_action.vote()
                bot.voted = True
                game.votes[vote].append(bot)
        vote_ja = "\n".join([player.name for player in game.votes['ja']])
        vote_nein = "\n".join([player.name for player in game.votes['nein']])
        if vote_ja == '':
            vote_ja = 'None!'
        if vote_nein == '':
            vote_nein = 'None!'
        fields = [{'name': 'Ja', 'value': vote_ja, 'inline': True}, {'name': 'Nein', 'value': vote_nein, 'inline': True}]
        await game.send_message('', title=f'Election of {game.nominee.name} as Chancellor - Voting Results', fields=fields, color=EmbedColor.INFO)
        results = len(game.votes['ja']) > len(game.votes['nein'])
        game.next_stage()
        await game.tick(voting_results=results)

async def tick(self, voting_results=None):
    # Stage: Nomination
    if self.stage == 'nomination':
        if not self.special_election:
            self.president = self.next_player
        else:
            self.special_election = False
        fields = [{
        'name': 'Valid Nominees',
        'value': '\n'.join(str(x) for x in self.valid_chancellors)
        }]
        await self.send_message(f'{self.president.name} is the President now!\nThey must nominate a Chancellor.', fields=fields)

        # Bot elects a chancellor
        if self.president.bot:
            self.nominee = bot_action.choose_chancellor(self.valid_chancellors)
            await self.send_message(f'{self.nominee.name} has been nominated to be the Chancellor! Send in your votes!')
            vote_msg = await self.send_message(title=f'0/{len(self.not_voted)} players voted.', color=EmbedColor.INFO)
            
            async def vote_handler(msg, player):
                vote, _ = await self.bot.wait_for('reaction_add', check=react_select(msg.id, player.id))
                vote = vote.emoji.name
                player.voted = True
                self.votes[vote].append(player)
                not_voted_msg = f'Waiting for: {", ".join(self.not_voted)}' if 0 < len(self.not_voted) <= 3 else ''
                await vote_msg.edit(embed=Embed(
                    title=f'{self.vote_count}/{self.vote_count + len(self.not_voted)} players voted.',
                    description=not_voted_msg,
                    color=EmbedColor.INFO))
                await vote_callback(self)

            vote_coros = []
            for player in self.players:
                if not player.bot:
                    image = image_merge(*map(utils.image_from_file, [self.asset_folder + f for f in ['vote_ja.png', 'vote_nein.png']]), pad=True)
                    msg = await self.send_message(description=f'Vote for election of {self.nominee.name} as Chancellor',
                        image=image, channel=player.dm_channel)
                    await msg.add_reaction(self.emojis['ja'])
                    await msg.add_reaction(self.emojis['nein'])
                    handler = vote_handler(msg, player)
                    vote_coros.append(handler)
            await asyncio.gather(*vote_coros)
        # Bot-only game, random voting results
        if all(player.bot for player in self.players):
            self.next_stage()
            await self.tick(voting_results=bot_action.vote()=='ja')

    # Stage: Election
    elif self.stage == 'election':
        if voting_results:
            self.chancellor_rejections = 0
            self.chancellor = self.nominee
            await self.send_message(f'The Chancellor was voted in! The President, {self.president.name}, must now send two policies to the Chancellor.', color=EmbedColor.SUCCESS)
            if self.board['fascist'] >= 3 and self.chancellor.identity == 'Hitler':
                message = f'Your new Chancellor {self.chancellor.name} was secretly Hitler, and with 3 or more fascist policies in place, the Fascists win!'
                await self.send_message(message, color=EmbedColor.ERROR)
                self.started = False
                # PLEASE UNCOMMENT THIS
                #return
            self.next_stage()
            await self.tick()
        else:
            self.chancellor_rejections += 1
            await self.send_message('The Chancellor was voted down!', color=EmbedColor.WARN)
            self.next_stage(skip=3)
            await self.tick()

    # Stage: President
    elif self.stage == 'president':
        self.policies = [self.policy_deck.pop() for _ in range(3)]
        policy_names = [policy.card_type.title() for policy in self.policies]
        message = ', '.join(policy_names)
        image = image_merge(*map(utils.image_from_file, [f'{self.asset_folder}{p.lower()}_policy.png' for p in policy_names]), pad=True)
        msg = await self.send_message(f'Choose two policies to send to the Chancellor, {self.chancellor.name}.',
            title=f'Policies: {message}', channel=self.president.dm_channel, footer=self.president.name if self.president.bot else '',
            image=image)
        if not self.president.bot:
            select_emojis = [self.emojis[str(i).zfill(2)] for i in range(1, 4)]
            for emoji in select_emojis:
                await msg.add_reaction(emoji)
            chancellor_policies = []
            while len(chancellor_policies) < 2:
                reaction, _ = await self.bot.wait_for('reaction_add', check=react_select(msg.id, self.president.id))
                policy_index = select_emojis.index(reaction.emoji)
                if policy_index not in chancellor_policies:
                    chancellor_policies.append(policy_index)
            self.policies = [self.policies[i] for i in sorted(chancellor_policies)]
        # Bot chooses two policies
        else:
            self.policies = bot_action.send_policies(self.policies)

        policy_names = [policy.card_type.title() for policy in self.policies]
        message = ', '.join(policy_names)
        image = image_merge(*map(utils.image_from_file, [f'{self.asset_folder}{p.lower()}_policy.png' for p in policy_names]), pad=True)
        
        await self.send_message(f'The President has sent two policies to the Chancellor, {self.chancellor.name}, who must now choose one to enact.', color=EmbedColor.SUCCESS)
        if self.board['fascist'] >= 5:
            await self.send_message('As there are at least 5 fascist policies enacted, the Chancellor may choose to invoke his veto power and discard both policies.')
            message += ' - Veto Allowed'
        
        self.enact_msg = await self.send_message('Choose a policy to enact.', title=f'Policies: {message}',
            channel=self.chancellor.dm_channel, footer=self.chancellor.name if self.chancellor.bot else '', image=image)
        self.next_stage()
        await self.tick()

    # Stage: Chancellor
    elif self.stage == 'chancellor':
        veto_msg = None
        # Bot enacts or vetoes a policy
        if self.chancellor.bot:
            enacted = bot_action.enact(self.policies)
            # Chancellor veto
            if self.board['fascist'] >= 5:
                self.chancellor.veto = bot_action.veto()
            if not self.chancellor.veto:
                self.board[enacted.card_type] += 1
                if enacted.card_type == 'fascist':
                    self.do_exec_act = True
                await self.send_message(f'A {enacted.card_type} policy was passed!', color=EmbedColor.SUCCESS)

        # Human reacts for enact / veto
        else:
            select_emojis = [self.emojis[str(i).zfill(2)] for i in range(1, 3)]
            if self.board['fascist'] >= 5:
                select_emojis.extend([self.emojis['veto']])
            msg = self.enact_msg
            for emoji in select_emojis:
                await msg.add_reaction(emoji)
            reaction, _ = await self.bot.wait_for('reaction_add', check=react_select(msg.id, self.chancellor.id))
            index = select_emojis.index(reaction.emoji)
            if index < 2:
                # Enact a policy if number is chosen
                enacted = self.policies[index]
                self.board[enacted.card_type] += 1
                if enacted.card_type == 'fascist':
                    self.do_exec_act = True
                await self.send_message(f'A {enacted.card_type} policy was passed!', color=EmbedColor.SUCCESS)
            else:
                # Otherwise, veto emoji is chosen
                self.chancellor.veto = True

        # President veto
        if self.chancellor.veto:
            veto_msg = await self.send_message('The Chancellor chooses to veto. The President must concur for the veto to go through.',
                color=EmbedColor.SUCCESS)
            if not self.president.bot:
                select_emojis = [self.emojis['yes'], self.emojis['no']]
                for emoji in select_emojis:
                    await veto_msg.add_reaction(emoji)
                reaction, _ = await self.bot.wait_for('reaction_add', check=react_select(veto_msg.id, self.president.id))
                index = select_emojis.index(reaction.emoji)
                self.president.veto = bool(index - 1)
            else:
                self.president.veto = bot_action.veto()

            if self.president.veto:
                await self.send_message('The President concurrs, and the veto is successful!', color=EmbedColor.SUCCESS)
            else:
                await self.game.send_message('The President does not concur, and the veto fails!', color=EmbedColor.WARN)
                select_emojis = [self.emojis[str(i).zfill(2)] for i in range(1, 3)]
                msg = self.enact_msg
                for emoji in select_emojis:
                    await msg.add_reaction(emoji)
                reaction, _ = await self.bot.wait_for('reaction_add', check=react_select(msg.id, self.chancellor.id))
                index = select_emojis.index(reaction.emoji)
                # Enact a policy if number is chosen
                enacted = self.policies[index]
                self.board[enacted.card_type] += 1
                if enacted.card_type == 'fascist':
                    self.do_exec_act = True
                await self.send_message(f'A {enacted.card_type} policy was passed!', color=EmbedColor.SUCCESS)
        
        self.next_stage()
        await self.tick()

    # Stage: Summary
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
        image = self.render_board()
        await self.send_message('', color=EmbedColor.INFO, image=image)

        if self.policy_count < 3:
            self.generate_deck()
            # I don't think it's necessary to say the deck was reshuffled.
            # await self.send_message('As the deck had less than three policies remaining, the deck has been reshuffled.', color=EmbedColor.INFO)
        
        if self.do_exec_act:
            self.do_exec_act = False
            await self.executive_action()
        else:
            await self.reset_rounds()
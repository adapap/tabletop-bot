# Discord
import discord
from discord import Embed
from discord.ext import commands

import asyncio
import functools
from . import bot_action
from . import verify
from game import Game
from utils import *

class Cog:
    def __init__(self, bot):
        self.bot = bot
        self.cardbot = bot.cardbot
        self.game = self.cardbot.game

    @commands.command()
    async def join(self, ctx, test_player: str='', repeat: int=1):
        """Joins the current running game."""
        if self.game.started:
            await self.game.send_message(f'You cannot join a game already running.', color=EmbedColor.ERROR)
            return
        player = ctx.author
        if test_player == 'bot':
            player = None
        for _ in range(repeat):
            await self.game.add_player(player)
            await asyncio.sleep(1)

    @commands.command()
    async def leave(self, ctx, bot_name: str=None):
        """Leaves the current game."""
        if self.game.started:
            await self.game.send_message('add leaving in middle of game... (this will break)')
        player = ctx.author
        bot = False
        if bot_name and bot_name in [b.name for b in self.game.bots]:
            player = bot_name
            bot = True
        await self.game.remove_player(player, bot=bot)

    # Game Commands
    @commands.command()
    @verify.game_started()
    @verify.stage('nomination')
    async def nominate(self, ctx, player: str=''):
        """Uses discord command $nominate to elect a chancellor."""
        member = None
        game = self.game
        if not game.stage == 'nomination':
            await game.send_message('It is not time to nominate.', color=EmbedColor.WARN)
        elif ctx.author.id != game.president.id:
            await game.send_message('You are not the President.', color=EmbedColor.WARN)
        elif player.startswith('Bot'):
            try:
                member = game.players[[player.name for player in game.players].index(player)]
            except ValueError:
                await game.send_message(f'There is no bot named {player}.', color=EmbedColor.ERROR)
        else:
            if len(ctx.message.mentions) != 1:
                await game.send_message('Invalid nomination. @mention the player you would like to nominate.', color=EmbedColor.WARN)
            else:
                member = game.find_player(ctx.message.mentions[0].id)
        # Logic
        if member == game.prev_president or member == game.prev_chancellor or member.id == ctx.author.id:
            await game.send_message('This player is ineligible to be nominated as Chancellor.\
                Please choose another chancellor.', color=EmbedColor.ERROR)
        else:
            game.nominee = member
            await game.send_message(f'{game.nominee.name} has been nominated to be the Chancellor! Send in your votes!')
            game.next_stage()

    @commands.command()
    @verify.game_started()
    @verify.stage('election')
    async def vote(self, ctx, vote: lower):
        """Reads votes from DMs to determine election status."""
        channel = ctx.message.channel
        game = self.game
        if not game.stage == 'election':
            await game.send_message('It is not time to vote.', color=EmbedColor.WARN)
        player = game.find_player(ctx.author.id).data
        if type(channel) == discord.channel.DMChannel:
            if vote not in ['ja', 'nein']:
                await ctx.send(embed=Embed(description='Your vote must either be "ja" or "nein".', color=EmbedColor.ERROR))
                return
            if player.voted:
                await ctx.send(embed=Embed(description='You have already voted for this round.', color=EmbedColor.WARN))
                return
            player.voted = True
            game.votes[vote].append(player)
            not_voted_msg = f'The following players have not voted yet: {", ".join(game.not_voted)}' if len(game.not_voted) <= 3 else ''
            await game.send_message(f'{game.vote_count}/{game.player_count} players voted. {not_voted_msg}')
        else:
            await ctx.message.delete()
            await self.game.send_message('Hey there! You might want to keep your vote private, so send it here instead.',
                color=EmbedColor.INFO, channel=ctx.author.dm_channel)
            return
        if len(game.not_voted) == game.bot_count:
            # Bots send in votes
            for bot in game.bots:
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
            await game.send_message('', title=f'Election of {self.game.nominee.name} as Chancellor - Voting Results', fields=fields, color=EmbedColor.INFO)
            results = len(game.votes['ja']) > len(game.votes['nein'])
            await game.tick(voting_results=results)

    @commands.command(aliases=['policy', 'send'])
    @verify.game_started()
    @verify.stage('president')
    async def send_policy(self, ctx, *policies: lower):
        """Send a policy given in the DM."""
        channel = ctx.message.channel
        player_dm = self.game.president.dm_channel
        given_policies = [p.card_type for p in self.game.policies]
        if ctx.author.id != self.game.president.id:
            return
        if not type(channel) == discord.channel.DMChannel:
            await ctx.message.delete()
            await self.game.send_message('Hey there! You might want to keep your policy selection private, so send it here instead.',
                color=EmbedColor.INFO, channel=ctx.author.dm_channel)
            return
        if len(policies) != 2:
            await self.game.send_message('You must choose exactly two policies to send.', channel=player_dm, color=EmbedColor.ERROR)
            return
        if any(policies.count(p) > given_policies.count(p) for p in policies):
            await self.game.send_message('You tried to send a policy that was not given to you.', channel=player_dm, color=EmbedColor.ERROR)
            return
        for policy in policies:
            if policy not in ['fascist', 'liberal']:
                await self.game.send_message('You must choose a "fascist" or "liberal" policy.', channel=player_dm, color=EmbedColor.ERROR)
                return
            self.game.policies.remove(given_policies.index(policy))
        await self.game.send_message(f'The President has sent two policies to the Chancellor,\
            {self.game.chancellor.name}, who must now choose one to enact.', color=EmbedColor.SUCCESS)
        message = ', '.join([policy.card_type.title() for policy in self.policies])
        if self.game.board['fascist'] >= 5:
            await self.send_message('As there are at least 5 fascist policies enacted, the Chancellor\
                may choose to invoke his veto power and discard both policies')
            message += ' - Veto Allowed'
        await self.game.send_message('Choose a policy to enact.', title=f'Policies: {message}',
            channel=self.chancellor.dm_channel, footer=self.chancellor.name, image='https://via.placeholder.com/500x250')
        self.game.next_stage()
        # Chancellor is a bot
        if self.game.chancellor.test_player:
            await self.tick()

    @commands.command(aliases=['enact'])
    @verify.game_started()
    @verify.stage('chancellor')
    async def enact_policy(self, ctx, policy: lower):
        """Choose a policy to enact given in the DM."""
        channel = ctx.message.channel
        player_dm = self.game.chancellor.dm_channel
        given_policies = [p.card_type for p in self.game.policies]
        if ctx.author.id != self.game.chancellor.id:
            return
        if not type(channel) == discord.channel.DMChannel:
            await ctx.message.delete()
            await self.game.send_message('Hey there! You might want to keep your policy selection private, so send it here instead.',
                color=EmbedColor.INFO, channel=ctx.author.dm_channel)
            return
        if policy not in given_policies:
            await self.game.send_message('You must enact a policy that was given to you.', channel=player_dm, color=EmbedColor.ERROR)
            return
        enacted = self.game.policies.pop(given_policies.index(policy))
        self.game.board[enacted.card_type] += 1
        await self.game.send_message(f'A {enacted.card_type} policy was passed!', color=EmbedColor.SUCCESS)

        if enacted.card_type == 'fascist':
            self.game.do_exec_act = True
        self.game.next_stage()
        await self.game.tick()

    @commands.command()
    @verify.game_started()
    @verify.stage('chancellor')
    async def veto(self, ctx, concur: lower='yes'):
        """Veto both policies received from the President."""
        chancellor = self.game.chancellor
        president = self.game.president
        if not chancellor.veto:
            if ctx.author.id == chancellor.id:
                chancellor.veto = True
                await self.game.send_message('The Chancellor chooses to veto. The President must concur for the veto to go through.',
                    color=EmbedColor.SUCCESS)
                # Check if President is bot
                if president.test_player:
                    await self.game.tick()
        elif not president.veto:
            if ctx.author.id == president.id and concur == 'yes':
                president.veto = True
                await self.game.send_message('The President concurrs, and the veto is successful!', color=EmbedColor.SUCCESS)
                self.game.next_stage()
                await self.game.tick()
            elif ctx.author.id == president.id:
                await self.game.send_message('The President does not concur, and the veto fails!', color=EmbedColor.WARN)
                self.game.next_stage()
                await self.game.tick()


def setup(bot):
    bot.add_cog(Cog(bot))
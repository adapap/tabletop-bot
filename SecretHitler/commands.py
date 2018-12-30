# Discord
import discord
from discord import Embed
from discord.ext import commands

import asyncio
import functools
from itertools import count
from random import shuffle, choice, sample, randint

from . import bot_action
from . import verify
from game import Game
from utils import *

uid_gen = count(-1, -1)
nametag_gen = iter(sample(range(100, 1000), 900))

class Cog:
    def __init__(self, bot):
        self.bot = bot
        self.game = self.bot.game

    @commands.command()
    async def join(self, ctx, bot: str='', repeat: int=1):
        """Joins the current running game."""
        if self.game.started:
            await self.game.send_message(f'You cannot join a game already running.', color=EmbedColor.ERROR)
            return
        for _ in range(repeat):
            member = ctx.author
            if bot == 'bot':
                member = discord.Object(id=str(next(uid_gen)))
                member.display_name = f'Bot{next(nametag_gen)}'
                member.dm_channel = None
                member.bot = True
            await self.game.add_player(member)
            await asyncio.sleep(1)

    @commands.command()
    async def leave(self, ctx, bot_name: str=None):
        """Leaves the current game."""
        if self.game.started:
            self.game.started = False
            await self.game.send_message('Game terminated due to player leaving the game.')
        player_id = ctx.author.id
        if bot_name in self.game.bots:
            player_id = self.game.bots[bot_name]
        await self.game.remove_player(player_id)

    # Game Commands
    @commands.command()
    @verify.game_started()
    @verify.stage('nomination')
    async def nominate(self, ctx, member: str=''):
        """Uses discord command $nominate to elect a chancellor."""
        player = None
        game = self.game
        if ctx.author.id != game.president.id:
            await game.send_message('You are not the President.', color=EmbedColor.WARN)
            return
        elif member.startswith('Bot'):
            if member not in game.bots:
                await game.send_message(f'There is no bot named {member}.', color=EmbedColor.ERROR)
                return
            else:
                bot_id = game.bots[member]
                player = game.find_player(bot_id)
        else:
            if len(ctx.message.mentions) != 1:
                await game.send_message('Invalid nomination. @mention the player you would like to nominate.', color=EmbedColor.WARN)
                return
            else:
                player = game.find_player(ctx.message.mentions[0].id)
        # Logic
        if player.had_position or player.id == ctx.author.id:
            await game.send_message('This player is ineligible to be nominated as Chancellor. Please choose another chancellor.', color=EmbedColor.ERROR)
            return
        else:
            game.nominee = player
            await game.send_message(f'{game.nominee.name} has been nominated to be the Chancellor! Send in your votes!')
            game.next_stage()

    # **Replaced with react voting system.**
    # @commands.command()
    # @verify.game_started()
    # @verify.stage('election')
    # async def vote(self, ctx, vote: lower):
    #     """Reads votes from DMs to determine election status."""
    #     channel = ctx.message.channel
    #     game = self.game
    #     player = game.find_player(ctx.author.id)
    #     # Rewrite using reaction voting (optionally?)
    #     if type(channel) == discord.channel.DMChannel:
    #         if vote not in ['ja', 'nein']:
    #             await ctx.send(embed=Embed(description='Your vote must either be "ja" or "nein".', color=EmbedColor.ERROR))
    #             return
    #         if player.voted:
    #             await ctx.send(embed=Embed(description='You have already voted for this round.', color=EmbedColor.WARN))
    #             return
    #         player.voted = True
    #         game.votes[vote].append(player)
    #         not_voted_msg = f'The following players have not voted yet: {", ".join(game.not_voted)}' if len(game.not_voted) <= 3 else ''
    #         await game.send_message(f'{game.vote_count}/{game.player_count - game.bot_count} players voted. {not_voted_msg}')
    #     else:
    #         await ctx.message.delete()
    #         await self.game.send_message('Hey there! You might want to keep your vote private, so send it here instead.',
    #             color=EmbedColor.INFO, channel=ctx.author.dm_channel)
    #         return
    #     if len(game.not_voted) == 0:
    #         if game.bot_count > 0:
    #             # Bots send in votes
    #             for bot in game.bots:
    #                 vote = bot_action.vote()
    #                 bot.voted = True
    #                 game.votes[vote].append(bot)
    #         vote_ja = "\n".join([player.name for player in game.votes['ja']])
    #         vote_nein = "\n".join([player.name for player in game.votes['nein']])
    #         if vote_ja == '':
    #             vote_ja = 'None!'
    #         if vote_nein == '':
    #             vote_nein = 'None!'
    #         fields = [{'name': 'Ja', 'value': vote_ja, 'inline': True}, {'name': 'Nein', 'value': vote_nein, 'inline': True}]
    #         await game.send_message('', title=f'Election of {self.game.nominee.name} as Chancellor - Voting Results', fields=fields, color=EmbedColor.INFO)
    #         results = len(game.votes['ja']) > len(game.votes['nein'])
    #         await game.tick(voting_results=results)

    @commands.command(aliases=['policy', 'send'])
    @verify.game_started()
    @verify.stage('president')
    async def send_policy(self, ctx, *policies: lower):
        """Send a policy given in the DM."""
        channel = ctx.message.channel
        game = self.game
        player_dm = game.president.dm_channel
        given_policies = [p.card_type for p in game.policies]
        policies = list(policies)
        if ctx.author.id != game.president.id:
            return
        if not type(channel) == discord.channel.DMChannel:
            await ctx.message.delete()
            await game.send_message('Hey there! You might want to keep your policy selection private, so send it here instead.',
                color=EmbedColor.INFO, channel=ctx.author.dm_channel)
            return
        if len(policies) != 2:
            await game.send_message('You must choose exactly two policies to send.', channel=player_dm, color=EmbedColor.ERROR)
            return
        if any(policies.count(p) > given_policies.count(p) for p in policies):
            await game.send_message('You tried to send a policy that was not given to you.', channel=player_dm, color=EmbedColor.ERROR)
            return
        for policy in policies:
            if policy not in ['fascist', 'liberal']:
                await game.send_message('You must choose a "fascist" or "liberal" policy.', channel=player_dm, color=EmbedColor.ERROR)
                return
        for policy_obj in self.game.policies[:]:
            if policy_obj.card_type in policies:
                policies.remove(policy_obj.card_type)
            else:
                game.policies.remove(policy_obj)
        await game.send_message(f'The President has sent two policies to the Chancellor, {game.chancellor.name}, who must now choose one to enact.', color=EmbedColor.SUCCESS)
        policy_names = [policy.card_type.title() for policy in game.policies]
        message = ', '.join(policy_names)
        image = image_merge(*[f'{p.lower()}_policy.png' for p in policy_names], asset_folder=game.asset_folder, pad=True)
        if game.board['fascist'] >= 5:
            await game.send_message('As there are at least 5 fascist policies enacted, the Chancellor may choose to invoke his veto power and discard both policies.')
            message += ' - Veto Allowed'
        await game.send_message('Choose a policy to enact.', title=f'Policies: {message}',
            channel=game.chancellor.dm_channel, footer=game.chancellor.name if game.chancellor.bot else '', image=image)
        game.next_stage()
        # Chancellor is a bot
        if game.chancellor.bot:
            await game.tick()

    @commands.command(aliases=['enact'])
    @verify.game_started()
    @verify.stage('chancellor')
    async def enact_policy(self, ctx, policy: lower):
        """Choose a policy to enact given in the DM."""
        channel = ctx.message.channel
        game = self.game
        player_dm = game.chancellor.dm_channel
        given_policies = [p.card_type for p in game.policies]
        if ctx.author.id != game.chancellor.id:
            return
        if not type(channel) == discord.channel.DMChannel:
            await ctx.message.delete()
            await game.send_message('Hey there! You might want to keep your policy selection private, so send it here instead.',
                color=EmbedColor.INFO, channel=ctx.author.dm_channel)
            return
        if policy not in given_policies:
            await game.send_message('You must enact a policy that was given to you.', channel=player_dm, color=EmbedColor.ERROR)
            return
        enacted = game.policies.pop(given_policies.index(policy))
        if enacted.card_type == 'fascist':
            game.do_exec_act = True
        game.board[enacted.card_type] += 1
        await game.send_message(f'A {enacted.card_type} policy was passed!', color=EmbedColor.SUCCESS)
        
        game.next_stage()
        await game.tick()

    @commands.command()
    @verify.game_started()
    @verify.stage('chancellor')
    async def veto(self, ctx, concur: lower='yes'):
        """Veto both policies received from the President."""
        game = self.game
        chancellor = game.chancellor
        president = game.president
        if not chancellor.veto:
            if ctx.author.id == chancellor.id:
                chancellor.veto = True
                await game.send_message('The Chancellor chooses to veto. The President must concur for the veto to go through.',
                    color=EmbedColor.SUCCESS)
                # Check if President is bot
                if president.bot:
                    await game.tick()
        elif not president.veto:
            if ctx.author.id == president.id and concur == 'yes':
                president.veto = True
                await game.send_message('The President concurrs, and the veto is successful!', color=EmbedColor.SUCCESS)
            elif ctx.author.id == president.id:
                await game.send_message('The President does not concur, and the veto fails!', color=EmbedColor.WARN)
            game.next_stage()
            await game.tick()

    @commands.command()
    @verify.game_started()
    @verify.stage('executive_action')
    async def execute(self, ctx, player: str=''):
        game = self.game
        if ctx.author.id != game.president.id:
            await game.send_message('You are not the President.', color=EmbedColor.WARN)
            return
        elif player.startswith('Bot'):
            try:
                member = game.players[[player.name for player in game.players].index(player)]
            except ValueError:
                await game.send_message(f'There is no bot named {player}.', color=EmbedColor.ERROR)
                return
        else:
            if len(ctx.message.mentions) != 1:
                await game.send_message('Invalid execution. @mention the player you would like to execute.', color=EmbedColor.WARN)
                return
            else:
                member = game.find_player(ctx.message.mentions[0].id)
                if not member:
                    await game.send_message('Invalid execution. Player is not in the game.', color=EmbedColor.WARN)
                    return
        
        if member == game.president:
            await game.send_message('You may not execute yourself!', color=EmbedColor.ERROR)
            return

        player_node = game.player_nodes.find(member.id, attr='id')
        game.player_nodes.remove(player_node)
        victim = player_node.data
        if member.identity == 'Hitler':
            await game.send_message(f'{victim.name} was executed. As he was Hitler, the Liberals win!')
            game.hitler_dead = True
            game.started = False
        else:
            await game.send_message(f'{victim.name} was executed.')
            await game.reset_rounds()

    @commands.command()
    @verify.game_started()
    @verify.stage('executive_action')
    async def appoint(self, ctx, player: str=''):
        game = self.game
        if ctx.author.id != game.president.id:
            await game.send_message('You are not the President.', color=EmbedColor.WARN)
            return
        elif player.startswith('Bot'):
            try:
                member = game.players[[player.name for player in game.players].index(player)]
            except ValueError:
                await game.send_message(f'There is no bot named {player}.', color=EmbedColor.ERROR)
                return
        else:
            if len(ctx.message.mentions) != 1:
                await game.send_message('Invalid appointment. @mention the player you would like to appoint.', color=EmbedColor.WARN)
                return
            else:
                member = game.find_player(ctx.message.mentions[0].id)
                if not member:
                    await game.send_message('Invalid appointment. Player is not in the game.', color=EmbedColor.WARN)
                    return
        
        if member == game.president:
            await game.send_message('You may not appoint yourself!', color=EmbedColor.ERROR)
            return

        player_node = game.player_nodes.find(member.id, attr='id')
        game.president.last_president = True
        new_president = player_node.data
        game.president = new_president
        game.special_election = True
        await game.send_message(f'{new_president.name} was appointed.')
        await game.reset_rounds()

    @commands.command()
    @verify.game_started()
    @verify.stage('executive_action')
    async def investigate(self, ctx, player: str=''):
        game = self.game
        if ctx.author.id != game.president.id:
            await game.send_message('You are not the President.', color=EmbedColor.WARN)
            return
        elif player.startswith('Bot'):
            try:
                member = game.players[[player.name for player in game.players].index(player)]
            except ValueError:
                await game.send_message(f'There is no bot named {player}.', color=EmbedColor.ERROR)
                return
        else:
            if len(ctx.message.mentions) != 1:
                await game.send_message('Invalid investigation. @mention the player you would like to appoint.', color=EmbedColor.WARN)
                return
            else:
                member = game.find_player(ctx.message.mentions[0].id)
                if not member:
                    await game.send_message('Invalid investigation. Player is not in the game.', color=EmbedColor.WARN)
                    return
        
        if member == game.president or member in game.previously_investigated:
            await game.send_message('You may not investigate yourself or a previously investigated player!', color=EmbedColor.ERROR)
            return

        player_node = game.player_nodes.find(member.id, attr='id')
        suspect = player_node.data
        game.previously_investigated.append(suspect)
        identity = suspect.identity if suspect.identity != 'Hitler' else 'Fascist'
        image = f'{identity.lower()}_{randint(0,5)}.png'
        await game.send_message(f'{suspect.name} is a {identity}.',
            channel=game.president.dm_channel, footer=game.president.name if game.president.bot else '', image=image)
        await game.reset_rounds()

def setup(bot):
    bot.add_cog(Cog(bot))
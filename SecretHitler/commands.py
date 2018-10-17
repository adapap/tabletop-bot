# Discord
import discord
from discord import Embed
from discord.ext import commands

import asyncio
from .bot_action import Bot as bot_action
from game import Game
from utils import EmbedColor

class Cog:
    def __init__(self, bot):
        self.bot = bot
        self.cardbot = bot.cardbot
        self.game = self.cardbot.game

    @commands.command(aliases=['test'])
    async def debug(self, ctx):
        pass

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
    async def leave(self, ctx):
        """Leaves the current game."""
        if self.game.started:
            await self.game.send_message('add leaving in middle of game... (this will break)')
        player = ctx.author
        await self.game.remove_player(player)

    # Game Commands
    @commands.command()
    async def nominate(self, ctx, player: str=''):
        """Uses discord command $nominate to elect a chancellor."""
        member = None
        game = self.game
        if not game.started:
            return
        if not game.stage == 'nomination':
            await game.send_message('It is not time to nominate.', color=EmbedColor.WARN)
        elif ctx.author.id != game.president.id:
            await game.send_message('You are not the President.', color=EmbedColor.WARN)
        elif player.startswith('Bot'):
            try:
                member = game.players[[player.name for player in game.players.elements].index(player)]
            except ValueError:
                await game.send_message(f'There is no bot named {player}.', color=EmbedColor.ERROR)
        else:
            if len(ctx.message.mentions) != 1:
                await game.send_message('Invalid nomination. @mention the player you would like to nominate.', color=EmbedColor.WARN)
            else:
                member = game.get_player(ctx.message.mentions[0].id)
        # Logic
        if member == game.prev_president or member == game.prev_chancellor or member.id == ctx.author.id:
            await game.send_message('This player is ineligible to be nominated as Chancellor.\
                Please choose another chancellor.', color=EmbedColor.ERROR)
        else:
            game.nominee = member
            await game.send_message(f'{game.nominee.name} has been nominated to be the Chancellor! Send in your votes!')
            game.stage = game.next_stage()

    @commands.command()
    async def vote(self, ctx, vote: str=''):
        """Reads votes from DMs to determine election status."""
        channel = ctx.message.channel
        game = self.game
        if not game.started:
            return
        if not game.stage == 'election':
            await game.send_message('It is not time to vote.', color=EmbedColor.WARN)
        player = game.players.find(ctx.author.id, attr='id').data
        if type(channel) == discord.channel.DMChannel:
            vote = vote.lower()
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
            await ctx.send(embed=Embed(
                description='Hey there! You might want to keep your vote private, so send it here instead.',
                color=EmbedColor.INFO))
        if len(game.not_voted) == game.bot_count:
            for bot in game.bots:
                vote = bot_action.vote()
                bot.voted = True
                game.votes[vote].append(bot)
            vote_ja = "\n".join([player.name for player in game.votes['ja']])
            vote_nein = "\n".join([player.name for player in game.votes['nein']])
            fields = [{'name': 'Ja', 'value': vote_ja, 'inline': True}, {'name': 'Nein', 'value': vote_nein, 'inline': True}]
            await game.send_message('', title='Voting Results', fields=fields, color=EmbedColor.INFO)
            results = len(game.votes['ja']) > len(game.votes['nein'])
            await game.tick(voting_results=results)

    @commands.Command(aliases=['policy'])
    async def send_policy(self, ctx, policy_name: str=''):
        """Send a policy given in the DM."""
        pass

def setup(bot):
    bot.add_cog(Cog(bot))
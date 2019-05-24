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
from .stages import *
from game import Game
from image import ImageUtil
from utils import *
import utils

uid_gen = count(-1, -1)
nametag_gen = iter(sample(range(100, 1000), 900))

class SecretHitler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game = self.bot.game

    @commands.command()
    async def join(self, ctx, bot: str='', repeat: int=1):
        """Joins the current running game."""
        if self.game.started:
            await self.game.error(f'You cannot join a game already running.')
            return
        for _ in range(repeat):
            member = ctx.author
            if bot == 'bot':
                member = discord.Object(id=str(next(uid_gen)))
                member.display_name = f'Bot{next(nametag_gen)}'
                member.dm_channel = None
                member.bot = True
            await self.game.add_player(member)
        if bot == 'bot':
            bots = ', '.join(name for name in self.game.bots)
            await self.game.message(f'{repeat} bot{"s" if repeat > 1 else ""} ({bots}) joined the game.')

    @commands.command()
    async def leave(self, ctx, bot_name: str=None):
        """Leaves the current game."""
        if self.game.started:
            self.game.started = False
            await self.game.message('Game terminated due to player leaving the game.')
        player_id = ctx.author.id
        if bot_name in self.game.bots:
            player_id = self.game.bots.pop(bot_name)
        await self.game.remove_player(player_id)

    # Game Commands
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
                await game.success('The Chancellor chooses to veto. The President must concur for the veto to go through.')
                # Check if President is bot
                if president.bot:
                    await game.tick()
        elif not president.veto:
            if ctx.author.id == president.id and concur == 'yes':
                president.veto = True
                await game.success('The President concurrs, and the veto is successful!')
            elif ctx.author.id == president.id:
                await game.warn('The President does not concur, and the veto fails!')
            game.next_stage()
            await game.tick()

    @commands.command()
    @verify.game_started()
    @verify.stage('execution')
    async def execute(self, ctx, player: str=''):
        game = self.game
        if ctx.author.id != game.president.id:
            await game.warn('You are not the President.')
            return
        elif player.startswith('Bot'):
            try:
                member = game.players[[player.name for player in game.players].index(player)]
            except ValueError:
                await game.error(f'There is no bot named {player}.')
                return
        else:
            if len(ctx.message.mentions) != 1:
                await game.warn('Invalid execution. @mention the player you would like to execute.')
                return
            else:
                member = game.find_player(ctx.message.mentions[0].id)
                if not member:
                    await game.warn('Invalid execution. Player is not in the game.')
                    return
        
        if member == game.president:
            await game.error('You may not execute yourself!')
            return

        player_node = game.player_nodes.find(member.id, attr='id')
        game.player_nodes.remove(player_node)
        victim = player_node.data
        if member.identity == 'Hitler':
            await game.message(f':knife: {victim.name} was executed. As he was Hitler, the Liberals win!')
            game.hitler_dead = True
            game.started = False
            return
        else:
            await game.message(f':knife: {victim.name} was executed.')
            await game.reset_rounds()

    @commands.command()
    @verify.game_started()
    @verify.stage('special_election')
    async def appoint(self, ctx, player: str=''):
        game = self.game
        if ctx.author.id != game.president.id:
            await game.warn('You are not the President.')
            return
        elif player.startswith('Bot'):
            try:
                member = game.players[[player.name for player in game.players].index(player)]
            except ValueError:
                await game.error(f'There is no bot named {player}.')
                return
        else:
            if len(ctx.message.mentions) != 1:
                await game.warn('Invalid appointment. @mention the player you would like to appoint.')
                return
            else:
                member = game.find_player(ctx.message.mentions[0].id)
                if not member:
                    await game.warn('Invalid appointment. Player is not in the game.')
                    return
        
        if member == game.president:
            await game.error('You may not appoint yourself!')
            return

        player_node = game.player_nodes.find(member.id, attr='id')
        game.president.last_president = True
        new_president = player_node.data
        game.president = new_president
        game.special_election = True
        await game.message(f'{new_president.name} was appointed.')
        await game.reset_rounds()

    @commands.command()
    @verify.game_started()
    @verify.stage('investigate_loyalty')
    async def investigate(self, ctx, player: str=''):
        game = self.game
        if ctx.author.id != game.president.id:
            await game.warn('You are not the President.')
            return
        elif player.startswith('Bot'):
            try:
                member = game.players[[player.name for player in game.players].index(player)]
            except ValueError:
                await game.error(f'There is no bot named {player}.')
                return
        else:
            if len(ctx.message.mentions) != 1:
                await game.warn('Invalid investigation. @mention the player you would like to appoint.')
                return
            else:
                member = game.find_player(ctx.message.mentions[0].id)
                if not member:
                    await game.warn('Invalid investigation. Player is not in the game.')
                    return
        
        if member == game.president or member in game.previously_investigated:
            await game.error('You may not investigate yourself or a previously investigated player!')
            return

        player_node = game.player_nodes.find(member.id, attr='id')
        suspect = player_node.data
        game.previously_investigated.append(suspect)
        identity = suspect.identity if suspect.identity != 'Hitler' else 'Fascist'
        image = f'party_{identity.lower()}.png'
        await game.message(f'{suspect.name} is a {identity}.', channel=game.president.dm_channel, footer=game.president.name, image=image)
        await game.reset_rounds()

def setup(bot):
    bot.add_cog(SecretHitler(bot))
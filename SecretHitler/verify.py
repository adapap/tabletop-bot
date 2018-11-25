from discord.ext import commands

def game_started():
    """Verifies that the game is running for a command."""
    async def predicate(ctx):
        return ctx.bot.game.started
    return commands.check(predicate)

def stage(stage):
    """Verifies that the game is in a current stage."""
    async def predicate(ctx):
        return ctx.bot.game.stage == stage
    return commands.check(predicate)
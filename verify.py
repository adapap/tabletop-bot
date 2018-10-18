from discord.ext import commands

def game_started():
    """Verifies that the game is running for a command."""
    async def predicate(ctx):
        return ctx.bot.cardbot.game.started
    return commands.check(predicate)
import discord
from typing import Awaitable, Callable

class Client:
    """Interface for interacting with various service APIs.
    
    Current integrations supported:
    Discord"""
    error: Callable
    info: Callable
    message: Callable[[str], Awaitable[None]]
    warn: Callable

class DiscordClient(Client, discord.Client):
    """Client interface for Zoom chatbots."""
    async def message(self, text: str) -> None:
        pass    

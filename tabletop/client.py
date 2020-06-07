import discord
from typing import Awaitable, Callable

class TabletopClient:
    """The client that handles running the different games supported by Tabletop."""
    error: Callable
    info: Callable
    message: Callable[[str], Awaitable[None]]
    warn: Callable

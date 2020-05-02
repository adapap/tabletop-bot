from typing import Callable, Literal

class Client:
    """Interface for interacting with various service APIs.
    
    Current integrations supported:
    None
    
    WIP:
    - Zoom
    - Discord"""
    message: Callable       

class ZoomClient(Client):
    """Client interface for Zoom chatbots."""
    async def message(self, text: str, *, type_: any):
        pass    

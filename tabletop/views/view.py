# Supports the following events:
"""Text
Info
Failure
Success
Create reactable
Image
Errors
"""

from . import MessageType
from typing import List
from PIL import Image

class View:
    """Console view is used to test the application through a command-line-interface.
    It can also be used to quickly debug code."""
    
    async def send_text(self, msg: str, msg_type: MessageType):
        """Sends text with specified type."""
        pass
        
    async def send_reactable(self, msg: str, options: List[str]) -> str:
        """Allows a user to submit a selection through an interface. 
        Returns a string with the user selection."""
        pass
    async def send_image(self, image_name: str):
        """Sends an image."""
        pass
    async def send_error(self, error_msg: str):
        """Sends an error message."""
        pass
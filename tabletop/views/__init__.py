import enum
import PIL
from typing import List

class MessageType(enum.Enum):
    """Enum for message types to be used in a view.
    - INFO: Contextual, informative message
    - FAILURE: Crticial message signalling an error or invalid action
    - SUCCESS: Message signalling of a completed event or valid action
    """ 
    INFO = 'INFO'
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCCESS'

class View:
    """Views support handling of events received from games. This includes displaying text or
    images, as well as receiving user input.
    
    A view must implement the following asynchronous methods:
    - `send_text(msg: str, msg_type: MessageType)`
    - `send_reactable(msg: str, options: List[str])`
    - `send_image(image: PIL.Image)`
    - `send_error(msg: str)`
    """
    async def send_text(self, msg: str, msg_type: MessageType):
        """Sends text with specified type."""
        raise NotImplementedError()
        
    async def send_reactable(self, msg: str, options: List[str]) -> str:
        """Allows a user to submit a selection through an interface. 
        Returns a string with the user selection."""
        raise NotImplementedError()
    
    async def send_image(self, image: PIL.Image):
        """Sends an image."""
        raise NotImplementedError()
    
    async def send_error(self, msg: str):
        """Sends an error message."""
        raise NotImplementedError()

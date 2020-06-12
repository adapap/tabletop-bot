import sys
import PIL
from . import MessageType, View
from typing import List

class ConsoleView(View):
    """Console view is used to test the application through a command-line-interface.
    It can also be used to quickly debug code."""
    
    async def send_text(self, msg: str, msg_type: MessageType):
        """Sends text message to standard output with type indicated in brackets."""
        sys.stdout.write(f'[{msg_type}] {msg}')
        
    async def send_reactable(self, msg: str, options: List[str]) -> str:
        """Allows a user to submit a selection through a GUI interface.
        Returns a string with the user selection."""
        sys.stdout.write(f'{msg}\n')
        for i, option in enumerate(options):
            sys.stdout.write(f'{i}. {msg}\n')
            selection = input('>')
        return selection

    async def send_image(self, image: PIL.Image):
        """Opens an image using the user's default image editor."""
        image.show()

    async def send_error(self, msg: str):
        """Sends error message to standard error."""
        sys.stderr.write(msg)

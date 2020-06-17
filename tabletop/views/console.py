import PIL.Image
import sys
from . import MessageType, View
from tabletop.util import Reactable
from typing import List

class ConsoleView(View):
    """Console view is used to test the application through a command-line-interface.
    It can also be used to quickly debug code."""
    
    async def send_text(self, msg: str, msg_type: MessageType):
        """Sends text message to standard output with type indicated in brackets."""
        sys.stdout.write(f'[{msg_type.name}] {msg}\n')
        
    async def send_reactable(self, reactable: Reactable) -> str:
        """Allows a user to submit a selection through a GUI interface.
        Returns a string with the user selection."""
        sys.stdout.write(f'{reactable.msg}\n')
        for i, option in enumerate(reactable.options):
            _, msg = option
            sys.stdout.write(f'{i + 1}. {msg}\n')
        while True:
            selection = input('> ')
            try:
                index = int(selection) - 1
                if not (0 <= index < len(reactable.options)):
                    raise ValueError
                key, _ = reactable.options[index]
                return key
            except ValueError:
                sys.stdout.write('Choose an option (number) from the list above.\n')

    async def send_image(self, image: PIL.Image):
        """Opens an image using the user's default image editor."""
        image.show()

    async def send_error(self, msg: str):
        """Sends error message to standard error."""
        sys.stderr.write(f'{msg}\n')

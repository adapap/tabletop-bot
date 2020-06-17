# to-do
# reactables have the following properties
# internal id
# list of menu options (index is key -> sent as response)
#   we can potentially use a map to provide custom keys instead of numerical index
# some way to return a value to the client
#   possibly a callback? awaitable?
from collections import defaultdict
from typing import DefaultDict, List, Tuple
from uuid import uuid4

ReactableOptions = List[Tuple[str, str]]
class Reactable:
    """Reactables are a way for the user to asynchronously provide
    input to the client. Options are passed as a list of key-value pairs,
    where the key is the return value of selecting the option, and the value
    is the data of selecting the value (probably an emoji name)."""
    def __init__(self, msg: str, options: ReactableOptions):
        self._id = uuid4()
        self.msg = msg
        self.counter: DefaultDict[str, int] = defaultdict(int)
        self.options = options
    
    async def create(self):
        pass
    
    async def react(self, option: str) -> str:
        pass

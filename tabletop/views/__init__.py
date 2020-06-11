import enum

class MessageType(enum.Enum):
    """Enum for message types to be used in a view.
    INFO: Contextual, informative message
    FAILURE: Crticial message signalling an error or invalid action
    SUCCESS: Message signalling of a completed event or valid action
    """ 
    INFO = 'INFO'
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCCESS'

class View:
    pass

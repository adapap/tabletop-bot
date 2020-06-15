# import discord
from typing import Optional
from tabletop.games import Game, GameCollection
from tabletop.views import MessageType, View

class Client:
    """The client that handles running the different games supported by Tabletop."""
    def __init__(self, view: View, games: GameCollection):
        self.view = view
        self.games = games
        self.game_index = 0
        
        self.current_game: Optional[Game] = None
        self.game_menu: Optional[str] = None
    
    @property
    def num_games(self):
        """The number of games available to play."""
        return len(self.games)

    async def connect(self):
        """Establishes a connection between the client and the view, allowing
        users to choose a game."""
        await self.view.send_text('Tabletop loaded!', MessageType.INFO)
        if self.games:
            msg = 'Select a game to play:'
            options = map(lambda x: x.name, self.games)
            self.game_menu = await self.view.send_reactable(msg, options)
        else:
            await self.view.send_error('No games found!')
            
    def next_game(self):
        """Event handler for scrolling to the next game in the collection."""
        self.game_index = (self.game_index + 1) % self.num_games
        print('[debug] next_game - reactable:', self.game_menu)
        
    def previous_game(self):
        """Event handler for scrolling to the previous game in the collection."""
        self.game_index = (self.game_index - 1) % self.num_games
        print('[debug] previous_game - reactable:', self.game_menu)

    async def start_game(self):
        """Event handler to start the current game selected."""
        print('[debug] starting current game...')
        self.current_game = self.games[self.game_index]()
        await self.current_game.on_start()
        
    async def stop_game(self):
        """Event handler to stop playing the current game."""
        print('[debug] stopping game...')
        await self.current_game.on_stop()

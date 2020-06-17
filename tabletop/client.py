# import discord
from typing import Optional, Sequence
from tabletop.games import Game, GameCollection
from tabletop.views import MessageType, View
from tabletop.util import Reactable

class Client:
    """The client that handles running the different games supported by Tabletop."""
    def __init__(self, view: View, games: GameCollection):
        self.view = view
        self.games = games
        
        self.current_game: Optional[Game] = None
        self.reactables: Sequence[Reactable] = []
    
    @property
    def num_games(self):
        """The number of games available to play."""
        return len(self.games)

    async def connect(self):
        """Establishes a connection between the client and the view, allowing
        users to choose a game using a menu."""
        await self.view.send_text('Tabletop loaded!', MessageType.INFO)
        if self.games:
            msg = 'Select a game to play:'
            options = [(x.name, x.name) for x in self.games]
            games = {x.name: x for x in self.games}
            reactable = Reactable(msg, options)
            game_name = await self.view.send_reactable(reactable)
            self.current_game = games[game_name](client=self)
            await self.start_game()
        else:
            await self.view.send_error('No games found!')
    
    # Possibly useless?        
    # async def run(self):
    #     """The main event loop of the client. Handles directing signals from
    #     games and views to each other, and manages user input from reactables."""
    #     while self.reactables:
    #         pass
    
    # This code should be used in the Discord view
    # def next_game(self):
    #     """Event handler for scrolling to the next game in the collection."""
    #     self.game_index = (self.game_index + 1) % self.num_games
    #     print('[debug] next_game - reactable:', self.game_menu)
        
    # def previous_game(self):
    #     """Event handler for scrolling to the previous game in the collection."""
    #     self.game_index = (self.game_index - 1) % self.num_games
    #     print('[debug] previous_game - reactable:', self.game_menu)

    async def start_game(self):
        """Event handler to start the current game selected."""
        print('[debug] starting current game...')
        await self.current_game.on_start()
        
    async def stop_game(self):
        """Event handler to stop playing the current game."""
        print('[debug] stopping game...')
        await self.current_game.on_stop()

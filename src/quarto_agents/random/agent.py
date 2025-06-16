from random import Random

from quarto_lib import (
    ChooseInitialPieceResponse,
    CompleteTurnResponse,
    GameState,
    Piece,
    QuartoAgent,
    get_available_cells,
    get_available_pieces,
)


class Agent(QuartoAgent):
    def __init__(self, seed: int | None = None):
        self.random = Random(seed)

    def choose_initial_piece(self) -> ChooseInitialPieceResponse:
        selected_piece = self.random.choice(list(Piece))
        return ChooseInitialPieceResponse(piece=selected_piece)

    def complete_turn(self, game: GameState) -> CompleteTurnResponse:
        cell = self.random.choice(list(get_available_cells(game)))
        piece = self.random.choice(list(get_available_pieces(game))) if get_available_pieces(game) else None
        return CompleteTurnResponse(cell=cell, piece=piece)

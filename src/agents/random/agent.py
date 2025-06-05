from random import Random
from typing import Optional, Tuple

from quarto_lib import Cell, GameState, InformalAgentInterface, Piece


class Agent(InformalAgentInterface):
    def __init__(self, seed: int | None = None):
        self.random = Random(seed)

    def choose_initial_piece(self) -> Piece:
        return self.random.choice(list(Piece))

    def complete_turn(self, game: GameState) -> Tuple[Cell, Optional[Piece]]:
        cell = self.random.choice(list(game.available_cells))
        piece = self.random.choice(list(game.available_pieces)) if game.available_pieces else None
        return cell, piece

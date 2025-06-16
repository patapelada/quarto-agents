import questionary
from quarto_lib import (
    ChooseInitialPieceResponse,
    CompleteTurnResponse,
    GameState,
    Piece,
    QuartoAgent,
    get_available_cells,
    get_available_pieces,
    piece_to_parts,
)

from agents.interactive.utils import draw_board, piece_to_unicode


class Agent(QuartoAgent):
    def __init__(self):
        super().__init__()

    def choose_initial_piece(
        self,
    ) -> ChooseInitialPieceResponse:
        choices = self.pieces_to_choices(list(Piece))
        selected_piece = questionary.select("Choose your initial piece:", choices=choices).ask()
        return ChooseInitialPieceResponse(piece=selected_piece)

    def complete_turn(self, game: GameState) -> CompleteTurnResponse:
        print("\033c", end="")  # ANSI escape code to clear the console
        print(draw_board(game.board))

        avaliable_pieces = get_available_pieces(game)
        print("Piece to place:", piece_to_unicode(game.current_piece))
        print(
            "Remaining pieces:",
            " ".join(piece_to_unicode(p) for p in sorted(avaliable_pieces, key=lambda p: p.value)),
        )
        cell_choices = [
            questionary.Choice(title=str(cell.name), value=cell)
            for cell in sorted(get_available_cells(game), key=lambda c: c.name)
        ]
        selected_cell = questionary.select("Choose a cell to place your piece:", choices=cell_choices).ask()

        updated_board = [row[:] for row in game.board]
        updated_board[selected_cell.row][selected_cell.col] = game.current_piece
        print("\033c", end="")  # ANSI escape code to clear the console
        print(draw_board(updated_board))

        pieces = list(avaliable_pieces)
        choices = self.pieces_to_choices(pieces)
        selected_piece = questionary.select("Choose a piece for your opponent:", choices=choices).ask()

        return CompleteTurnResponse(cell=selected_cell, piece=selected_piece)

    @staticmethod
    def pieces_to_choices(pieces: list[Piece]) -> list[questionary.Choice]:
        choices: list[questionary.Choice] = []
        for piece in sorted(pieces, key=lambda p: p.value):
            char, _, color, prefix, suffix = piece_to_parts(piece)
            choice = questionary.Choice(
                title=[
                    ("fg:#000000", prefix),
                    ("fg:#f44336", char) if color == 0 else ("fg:#2196f3", char),
                    ("fg:#000000", suffix),
                ],
                value=piece,
            )
            choices.append(choice)
        return choices

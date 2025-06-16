from typing import List, Optional

from quarto_lib import Piece, piece_to_parts
from tabulate import tabulate
from termcolor import colored


def piece_to_unicode(piece: Piece) -> str:
    char, template, color, prefix, suffix = piece_to_parts(piece)
    colored_char = colored(char, "red" if color == 0 else "blue")

    return template.format(char=colored_char, prefix=prefix, suffix=suffix)


def draw_board(board: List[List[Optional[Piece]]]) -> str:
    side = ["1", "2", "3", "4"]
    footer = ["A", "B", "C", "D"]
    board_display = [["" for _ in range(5)] for _ in range(5)]
    for i in range(5):
        for j in range(5):
            if i == 4 and j == 0:
                board_display[i][j] = " "
            elif i == 4:
                board_display[i][j] = footer[j - 1]
            elif j == 0:
                board_display[i][j] = side[3 - i]
            else:
                piece = board[i][j - 1]
                if piece is None:
                    board_display[i][j] = "...."
                else:
                    board_display[i][j] = piece_to_unicode(piece)

    return tabulate(
        board_display,
        tablefmt="grid",
        stralign="center",
        numalign="center",
    )

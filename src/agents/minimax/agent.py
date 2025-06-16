import logging
from enum import Enum
from random import Random
from typing import Callable, Optional, Tuple

from quarto_lib import (
    Board,
    Cell,
    ChooseInitialPieceResponse,
    CompleteTurnResponse,
    GameState,
    Piece,
    QuartoAgent,
    check_win,
    common_characteristics,
    get_all_lines,
    get_available_cells,
    get_available_pieces,
)

logger = logging.getLogger(__name__)


class Agent(QuartoAgent):
    WIN_SCORE = 1000
    LOSE_SCORE = -1000
    GAME_STATE_CACHE_KEY = Tuple[Tuple[Tuple[Optional[Piece], ...], ...], Optional[Piece], bool, int]
    MINIMAX_EVALUATION_RESULT = Tuple[float, Optional[Cell], Optional[Piece]]

    def __init__(
        self,
        depth_limits: Tuple[int, int, int] = (2, 3, 5),
    ):
        super().__init__()
        logger.info("Initializing Minimax Agent")
        self.depth_limits = depth_limits
        self._random = Random()
        self.cache: dict[Agent.GAME_STATE_CACHE_KEY, Agent.MINIMAX_EVALUATION_RESULT] = {}

    def choose_initial_piece(self) -> ChooseInitialPieceResponse:
        selected_piece = self._random.choice(list(Piece))
        return ChooseInitialPieceResponse(piece=selected_piece)

    def complete_turn(self, game: GameState) -> CompleteTurnResponse:
        # Assess game phase
        game_phase = self.evaluate_game_phase(game)
        logger.debug("Game phase evaluated as: %s (%d | 16)", game_phase.name, len(get_available_cells(game)))

        depth_limit = self.depth_limits[0]

        def evaluation_function(board: Board) -> int:
            return self.evaluate_board(board)

        if game_phase == self.GamePhase.EARLY_GAME:

            def evaluation_function(board: Board) -> int:
                return self.evaluate_board(board) * -1

        if game_phase == self.GamePhase.LATE_GAME:
            depth_limit = self.depth_limits[2]

        elif game_phase == self.GamePhase.MID_GAME:
            depth_limit = self.depth_limits[1]

        score, cell, piece = self.minimax(
            game.board,
            get_available_pieces(game),
            get_available_cells(game),
            game.current_piece,
            True,
            depth_limit,
            cache=self.cache,
            evaluation_function=evaluation_function,
        )
        logger.debug("Minimax completed with score: %s, cell: %s, piece: %s", score, cell, piece)

        if cell is None:
            raise ValueError("No valid move found. This should not happen with a properly implemented minimax.")

        return CompleteTurnResponse(
            cell=cell,
            piece=piece,
        )

    @classmethod
    def minimax(
        cls,
        board: Board,
        available_pieces: set[Piece],
        available_cells: set[Cell],
        current_piece: Optional[Piece],
        maximizing: bool,
        depth: int,
        cache: dict[GAME_STATE_CACHE_KEY, MINIMAX_EVALUATION_RESULT],
        evaluation_function: Callable[[Board], int],
        alpha: float = float("-inf"),
        beta: float = float("inf"),
    ) -> MINIMAX_EVALUATION_RESULT:
        if check_win(board):
            return (cls.WIN_SCORE if not maximizing else cls.LOSE_SCORE), None, None
        key = (tuple(tuple(row) for row in board), current_piece, maximizing, depth)
        if key in cache:
            return cache[key]
        if not available_pieces or depth == 0:
            eval_score = evaluation_function(board)
            return eval_score, None, None

        best_score = float("-inf") if maximizing else float("inf")
        best_move = None
        best_piece_to_give = None

        for cell in available_cells:
            board[cell.row][cell.col] = current_piece

            for next_piece in available_pieces:
                new_avail = available_pieces - {next_piece}
                new_cells = available_cells - {cell}
                score, _, _ = cls.minimax(
                    board,
                    new_avail,
                    new_cells,
                    next_piece,
                    not maximizing,
                    depth - 1,
                    cache,
                    evaluation_function=evaluation_function,
                    alpha=alpha,
                    beta=beta,
                )

                if maximizing:
                    if score > best_score:
                        best_score = score
                        best_move = cell
                        best_piece_to_give = next_piece
                    alpha = max(alpha, best_score)
                else:
                    if score < best_score:
                        best_score = score
                        best_move = cell
                        best_piece_to_give = next_piece
                    beta = min(beta, best_score)

                if beta <= alpha:
                    break  # prune

            board[cell.row][cell.col] = None  # undo move

            if beta <= alpha:
                break  # prune outer loop too

        cache[key] = (best_score, best_move, best_piece_to_give)
        return cache[key]

    @classmethod
    def evaluate_board(cls, board: Board) -> int:
        """
        Heuristic evaluation of a Quarto board.
        +10 for each line with 3 same-bit pieces and one empty
        +3 for each line with 2 same-bit pieces
        """
        score = 0
        lines = get_all_lines(board)

        for line in lines:
            pieces = [p for p in line if p is not None]
            if common_characteristics(pieces):
                if len(pieces) == 3:
                    score += 10
                elif len(pieces) == 2:
                    score += 3

        return score

    class GamePhase(Enum):
        EARLY_GAME = 1
        MID_GAME = 2
        LATE_GAME = 3

    @classmethod
    def evaluate_game_phase(cls, game: GameState) -> GamePhase:
        lines = get_all_lines(game.board)
        lines_with_common_pieces = [line if common_characteristics(line) else [] for line in lines]
        n_three_same = sum(1 for line in lines_with_common_pieces if len([p for p in line if p is not None]) == 3)
        n_two_same = sum(1 for line in lines_with_common_pieces if len([p for p in line if p is not None]) == 2)

        if n_three_same > 2 or len(get_available_cells(game)) <= 8:
            return cls.GamePhase.LATE_GAME
        if n_two_same > 0:
            return cls.GamePhase.MID_GAME
        return cls.GamePhase.EARLY_GAME

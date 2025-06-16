import logging

from quarto_lib import Arena

from quarto_agents.interactive.agent import Agent as InteractiveAgent
from quarto_agents.interactive.utils import draw_board
from quarto_agents.minimax.agent import Agent as MiniMaxAgent

logging.basicConfig(level=logging.INFO)


def launch_game():
    print("\033c", end="")  # ANSI escape code to clear the console
    arena = Arena(InteractiveAgent(), MiniMaxAgent(depth_limits=(2, 3, 5)))
    arena.play()

    print("\033c", end="")
    print("Game Over!")
    print(draw_board(arena.game.board))


if __name__ == "__main__":
    launch_game()

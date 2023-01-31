import time

from state_calculator import StateCalculator
from game_state import GameState
from bsnes_game import Game


if __name__ == "__main__":
    game = Game()
    while True:
        game.restart_game()
        calculator = StateCalculator(GameState(None, None, initial_game=game))
        calculator.start()
        time.sleep(1)
        while not game.is_game_live(): pass
        while game.is_game_live():
            calculator.stop()
            calculator.join()
            calculated_moves = calculator.best_state.moves
            if not calculated_moves:
                [game.perform_raise() for _ in range(8)]
            else:
                game.perform_moves(calculated_moves)
            time.sleep(5)
            print(f"Actual")
            GameState(None, None, initial_game=game).print_board()
        calculator.stop()

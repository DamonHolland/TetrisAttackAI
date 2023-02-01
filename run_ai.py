import heapq
import threading
import time

from game_state import GameState
from bsnes_game import Game


class StateCalculator(threading.Thread):
    def __init__(self, initial_state: GameState):
        threading.Thread.__init__(self)
        self.best_state = initial_state
        self._search_queue = []
        self._stop_request = threading.Event()

    def run(self):
        self._search_queue = [self.best_state]
        print(f"Initial")
        self.best_state.print_board()
        while not self._stop_request.is_set():
            for new_state in heapq.heappop(self._search_queue).get_valid_children():
                if self._stop_request.is_set(): return
                if new_state.fitness > self.best_state.fitness:
                    self.best_state = new_state
                heapq.heappush(self._search_queue, new_state)

    def stop(self):
        print(f"Scanned: {len(self._search_queue)} Best: {self.best_state.moves}, Fitness: {self.best_state.fitness}")
        print(self.best_state.chain)
        print(self.best_state.combos)
        self._stop_request.set()


if __name__ == "__main__":
    game = Game()
    while True:
        game.restart_game()
        calculator = StateCalculator(GameState(None, None, game.get_tile_map(), game.get_chain()))
        calculator.start()
        while not game.is_game_live(): pass
        while game.is_game_live():
            time.sleep(0.3)
            calculator.stop()
            calculator.join()
            calculated_state = calculator.best_state
            if not calculated_state.moves:
                [game.perform_raise() for _ in range(8)]
            else:
                game.perform_moves(calculated_state.moves)
            calculator = StateCalculator(GameState(None, None, game.get_tile_map(), game.get_chain()))
            calculator.start()
        calculator.stop()

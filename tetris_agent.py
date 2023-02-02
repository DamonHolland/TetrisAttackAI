import heapq
import time

from bsnes_game import Game
from fitness_evaluator import FitnessEvaluator
from game_state import GameState


class TetrisAgent:
    def __init__(self, game: Game, evaluator: FitnessEvaluator, evaluation_time_limit: int = 200000000):
        self.game = game
        self.evaluator = evaluator
        self.evaluation_time_limit = evaluation_time_limit

    def play_game(self) -> int:
        time.sleep(0.2)
        self.game.restart_game()
        while self.game.is_game_live():
            best_state = GameState(self.evaluator, None, None, self.game.get_tile_map(), self.game.get_chain())
            search_queue = [best_state]
            end_time = time.perf_counter_ns() + self.evaluation_time_limit
            while time.perf_counter_ns() < end_time:
                explore_children = heapq.heappop(search_queue).get_valid_children()
                if not explore_children:
                    break
                for new_state in explore_children:
                    if new_state.fitness > best_state.fitness:
                        best_state = new_state
                    heapq.heappush(search_queue, new_state)
            print(f"Scanned: {len(search_queue)} Best: {best_state.moves}")
            self.game.perform_moves(best_state.moves)
        return self.game.get_score()

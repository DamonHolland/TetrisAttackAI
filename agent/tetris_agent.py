import heapq
import sys
import time

from game.bsnes_game import Game
from agent.evaluators.fitness_evaluator import FitnessEvaluator
from game.game_state import GameState


class TetrisAgent:
    def __init__(self, game: Game, evaluator: FitnessEvaluator, evaluation_time_limit: int = 200000000):
        self.game = game
        self.evaluator = evaluator
        self.evaluation_time_limit = evaluation_time_limit

    def play_game(self, time_limit: int = sys.maxsize) -> int:
        self.game.restart_game()
        start_time = time.perf_counter()
        while self.game.is_game_live() and time.perf_counter() - start_time < time_limit:
            best_state = GameState(self.evaluator, None, None, self.game.get_tile_map(),
                                   self.game.get_chain(), (self.game.get_cursor_x(), self.game.get_cursor_y()))
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

            if self.evaluator.should_raise(best_state.get_metrics()):
                self.game.perform_raise()
            else:
                self.game.perform_moves(best_state.moves)
        final_score = self.game.get_score()
        print(f"Game over, final score: {final_score}")
        return final_score

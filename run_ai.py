import heapq
import time
import cProfile

from game_state import GameState
from bsnes_game import Game


def find_best(initial_state, time_ns):
    best_state = initial_state
    search_queue = [best_state]
    end_time = time.perf_counter_ns() + time_ns
    while time.perf_counter_ns() < end_time:
        explore_state = heapq.heappop(search_queue)
        explore_children = explore_state.get_valid_children()
        if not explore_children:
            break
        for new_state in explore_children:
            if new_state.fitness > best_state.fitness:
                best_state = new_state
            heapq.heappush(search_queue, new_state)
    print(f"Scanned: {len(search_queue)} Best: {best_state.moves}")
    return best_state


def main():
    game = Game()
    while True:
        calculated_state = find_best(GameState(None, None, game.get_tile_map(), game.get_chain()), 200000000)
        game.perform_moves(calculated_state.moves)


if __name__ == "__main__":
    cProfile.run("main()", sort="tottime")

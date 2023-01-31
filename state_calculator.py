import heapq
import threading
from game_state import GameState


class StateCalculator(threading.Thread):
    def __init__(self, initial_state: GameState):
        threading.Thread.__init__(self)
        self.best_state = initial_state
        self.best_fitness = initial_state.fitness
        self.stop_request = threading.Event()
        self._search_queue = []

    def run(self):
        self._search_queue = [self.best_state]
        print(f"Initial")
        self.best_state.print_board()
        while not self.stop_request.is_set():
            explore_state = heapq.heappop(self._search_queue)
            for new_state in explore_state.get_valid_children():
                if self.stop_request.is_set(): return
                if new_state.fitness > self.best_fitness:
                    self.best_fitness = new_state.fitness
                    self.best_state = new_state
                heapq.heappush(self._search_queue, new_state)

    def stop(self):
        print(f"Scanned: {len(self._search_queue)} Best: {self.best_state.moves}, Fitness: {self.best_state.fitness}")
        print(f"Expected")
        self.best_state.print_board()
        self.stop_request.set()

import copy

from bsnes_game import Game


class GameState:
    MOVE_OPTIONS = [(i, j) for i in range(5) for j in range(11)]
    BOARD_WIDTH = 6
    BOARD_HEIGHT = 12
    COMBO_SCORE = {3: 30, 4: 60, 5: 80, 6: 200, 7: 230, 8: 250, 9: 400, 10: 600, 11: 800, 12: 1000}
    CHAIN_SCORE = {2: 50, 3: 80, 4: 150, 5: 300, 6: 400, 7: 500, 8: 700, 9: 900, 10: 1100, 11: 1300, 12: 1500, 13: 1800}

    def __init__(self, parent: 'GameState' or None, new_move: tuple[int, int] or None, initial_game: Game = None):
        # Initial state initialisation
        self.parent: GameState = parent
        if not initial_game:
            self.initial_state = self.parent.initial_state
            self.moves: list[tuple[int, int]] = self.parent.moves + [new_move]
            self.starting_chain = self.parent.starting_chain
        else:
            self.initial_state = initial_game.get_tile_map()
            self.moves: list[tuple[int, int]] = []
            self.starting_chain = initial_game.get_chain()
        self.state: list[list[int]] = copy.deepcopy(self.initial_state)
        self.combos: list[int] = list()
        self.chains: list[int] = list()
        self.locked_cells: set[tuple[int, int]] = set()
        self._fitness = None

        # Pre-gravity checks
        for x, y in self.moves:
            self.state[y][x], self.state[y][x + 1] = self.state[y][x + 1], self.state[y][x]
            self.combos.append(self.simulate_combo(lock_cells=True))
        self.gravity_lock(len(self.moves) <= 2)

    def __lt__(self, other):
        return (0 - self.fitness) < (0 - other.fitness)

    def simulate_combo(self, lock_cells: bool = False) -> int:
        combo = set()
        for j in range(self.BOARD_WIDTH):
            for i in range(self.BOARD_HEIGHT):
                if j < self.BOARD_WIDTH - 2:
                    if self.state[i][j] and self.state[i][j] == self.state[i][j + 1] == self.state[i][j + 2]:
                        combo.update((j + o, i) for o in range(3))
                if i < self.BOARD_HEIGHT - 2:
                    if self.state[i][j] and self.state[i][j] == self.state[i + 1][j] == self.state[i + 2][j]:
                        combo.update((j, i + o) for o in range(3))
        for cell in combo:
            if lock_cells:
                self.locked_cells.add(cell)
            self.state[cell[1]][cell[0]] = 0
        return len(combo)

    def simulate_chains(self) -> int:
        current_chain = self.starting_chain
        while True:
            self.simulate_gravity()
            if not (combo := self.simulate_combo()): break
            current_chain += 1
            self.combos.append(combo)
        return current_chain

    def simulate_gravity(self):
        for col in range(self.BOARD_WIDTH):
            for row in range(1, self.BOARD_HEIGHT):
                if self.state[row][col] == 0:
                    for gr in range(row, self.BOARD_HEIGHT):
                        if self.state[gr][col]:
                            self.state[row - 1][col] = self.state[gr][col]
                            self.state[gr][col] = 0
                            break

    def gravity_lock(self, above_only: bool = False):
        falling_cols = {}
        for col in range(self.BOARD_WIDTH):
            for row in range(self.BOARD_HEIGHT - 1):
                if self.state[row][col]: continue
                hole_pos = row
                for gr in range(row, self.BOARD_HEIGHT - 1):
                    if self.state[gr][col]:
                        if (col, gr) in self.locked_cells:
                            if col in falling_cols.keys():
                                falling_cols.pop(col)
                                break
                        else:
                            if col not in falling_cols.keys():
                                falling_cols[col] = (hole_pos, gr)
        for col, locked_bottom in falling_cols.items():
            self.locked_cells.update((col, locked_row) for locked_row in range(locked_bottom[int(above_only)], self.BOARD_HEIGHT))

    def get_height_metrics(self) -> tuple[int, int]:
        col_heights = []
        for c in range(self.BOARD_WIDTH):
            for r in range(self.BOARD_HEIGHT):
                if self.state[r][c] != 0: continue
                col_heights.append(r)
                break
        return max(col_heights), sum(abs(a - b) for a, b in zip(col_heights, col_heights[1:]))

    @property
    def fitness(self) -> int:
        if self._fitness: return self._fitness
        self.chains = [chain for chain in range(self.simulate_chains())]
        chain_score = sum(self.CHAIN_SCORE.get(chain_num, 0) for chain_num in self.chains)
        combo_score = sum(self.COMBO_SCORE.get(combo, 0) for combo in self.combos)
        tallest, roughness = self.get_height_metrics()
        self._fitness = chain_score + combo_score - (tallest * 10) - (len(self.moves) * 2) - (roughness * 6)
        return self._fitness

    def print_board(self):
        print(''.center(11, '-'))
        for row in self.state[::-1]:
            for cell in row:
                print(cell, end=" ")
            print()
        print(''.center(11, '-'))

    def get_valid_children(self) -> list['GameState']:
        valid = [m for m in self.MOVE_OPTIONS if m not in self.locked_cells
                 and (m[0] + 1, m[1]) not in self.locked_cells and self.state[m[1]][m[0]] != self.state[m[1]][m[0] + 1]]
        return [GameState(self, m) for m in valid]

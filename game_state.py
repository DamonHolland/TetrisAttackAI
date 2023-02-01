import copy


class GameState:
    MOVE_OPTIONS = [(i, j) for i in range(5) for j in range(11)]
    BOARD_WIDTH = 6
    BOARD_HEIGHT = 12
    COMBO_SCORE = {3: 30, 4: 60, 5: 80, 6: 200, 7: 230, 8: 250, 9: 400, 10: 600, 11: 800, 12: 1000}
    CHAIN_SCORE = {2: 50, 3: 80, 4: 150, 5: 300, 6: 400, 7: 500, 8: 700, 9: 900, 10: 1100, 11: 1300, 12: 1500, 13: 1800}

    def __init__(self, parent: 'GameState' or None, new_move: tuple[int, int] or None,
                 initial_tiles: list[list[int]] = None, initial_chain: int = None):
        # Initial state initialisation
        self.parent: GameState = parent
        if parent:
            self.initial_state: list[list[int]] = self.parent.initial_state
            self.moves: list[tuple[int, int]] = self.parent.moves + [new_move]
            self.initial_chain = self.parent.initial_chain
        else:
            self.initial_state: list[list[int]] = initial_tiles
            self.moves: list[tuple[int, int]] = []
            self.initial_chain = initial_chain
        self.chain: int = self.initial_chain
        self.state: list[list[int]] = copy.deepcopy(self.initial_state)
        self.combos: list[int] = list()
        self.locked_cells: set[tuple[int, int]] = set()
        self._fitness = None

        # Pre-gravity checks
        for x, y in self.moves:
            self.state[x][y], self.state[x + 1][y] = self.state[x + 1][y], self.state[x][y]
            self.simulate_combo(lock_cells=True)
        self.lock_gravity_affected_cells(len(self.moves))

        # Post-gravity checks
        self.simulate_gravity()
        if self.simulate_combo():
            self.chain += 1

    def __lt__(self, other):
        return (0 - self.fitness) < (0 - other.fitness)

    def simulate_combo(self, lock_cells: bool = False) -> bool:
        combo = set()
        for col in range(self.BOARD_WIDTH):
            for row in range(self.BOARD_HEIGHT - 2):
                if self.state[col][row] and self.state[col][row] == self.state[col][row + 1] == self.state[col][row + 2]:
                    combo.update((col, row + i) for i in range(3))
        for row in range(self.BOARD_HEIGHT):
            for col in range(self.BOARD_WIDTH - 2):
                if self.state[col][row] and self.state[col][row] == self.state[col + 1][row] == self.state[col + 2][row]:
                    combo.update((col + i, row) for i in range(3))

        combo_len = len(combo)
        if combo_len > 0:
            for cell in combo:
                if lock_cells:
                    self.locked_cells.add(cell)
                self.state[cell[0]][cell[1]] = 0
            self.combos.append(combo_len)
        return combo_len != 0

    def simulate_gravity(self):
        for col in range(self.BOARD_WIDTH):
            if 0 in self.state[col]:
                stripped_col = [cell for cell in self.state[col] if cell]
                stripped_col += [0] * (self.BOARD_HEIGHT - len(stripped_col))
                self.state[col] = stripped_col

    def lock_gravity_affected_cells(self, gravity_depth: int = 1):
        for col_num, col in enumerate(self.state):
            for i in range(self.BOARD_HEIGHT - 1, -1, -1):
                if not col[i] or (col_num, i) in self.locked_cells:
                    continue
                for j in range(i-1, max(-1, i-gravity_depth-1), -1):
                    if (col_num, j) in self.locked_cells:
                        break
                    if not col[j]:
                        self.locked_cells.update({(col_num, row_num) for row_num in range(j, i)})
                        break

    def get_height_metrics(self) -> tuple[int, int]:
        col_heights = []
        for c in range(self.BOARD_WIDTH):
            for r in range(self.BOARD_HEIGHT):
                if self.state[c][r] != 0: continue
                col_heights.append(r)
                break
        return max(col_heights), sum(abs(a - b) for a, b in zip(col_heights, col_heights[1:]))

    @property
    def fitness(self) -> int:
        if self._fitness: return self._fitness
        chain_score = sum(self.CHAIN_SCORE.get(chain, 0) for chain in range(self.chain))
        combo_score = sum(self.COMBO_SCORE.get(combo, 0) for combo in self.combos)
        tallest, roughness = self.get_height_metrics()
        self._fitness = chain_score + combo_score - (tallest * 10) - (roughness * 5) - len(self.moves)
        return self._fitness

    def print_board(self):
        print(''.center(11, '-'))
        for row in range(self.BOARD_HEIGHT - 1, -1, -1):
            for col in range(self.BOARD_WIDTH):
                print(self.state[col][row], end=" ")
            print()
        print(''.center(11, '-'))

    def get_valid_children(self) -> list['GameState']:
        valid = [m for m in self.MOVE_OPTIONS if m not in self.locked_cells
                 and (m[0] + 1, m[1]) not in self.locked_cells and self.state[m[0]][m[1]] != self.state[m[0] + 1][m[1]]]
        return [GameState(self, m) for m in valid]

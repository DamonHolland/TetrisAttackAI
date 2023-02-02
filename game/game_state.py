from agent.evaluators.fitness_evaluator import FitnessEvaluator


def custom_deepcopy(lst):
    return [list(map(int, row)) for row in lst]


class GameState:
    MOVE_OPTIONS = [(i, j) for i in range(5) for j in range(11)]
    BOARD_WIDTH = 6
    BOARD_HEIGHT = 12

    def __init__(self, evaluator: FitnessEvaluator, parent: 'GameState' or None, new_move: tuple[int, int] or None,
                 initial_tiles: list[list[int]] = None, initial_chain: int = None,
                 initial_cursor: tuple[int, int] or None = None, terminal: bool = False):
        # Initial state initialisation
        self.parent: GameState = parent
        if parent:
            self.initial_state: list[list[int]] = self.parent.initial_state
            self.moves: list[tuple[int, int]] = self.parent.moves + [new_move]
            self.initial_chain = self.parent.initial_chain
            self.initial_cursor: tuple[int, int] = self.parent.initial_cursor
        else:
            self.initial_state: list[list[int]] = initial_tiles
            self.moves: list[tuple[int, int]] = []
            self.initial_chain = initial_chain
            self.initial_cursor: tuple[int, int] = initial_cursor
        self.evaluator = evaluator
        self.chain: int = self.initial_chain
        self.state: list[list[int]] = custom_deepcopy(self.initial_state)
        self.combos: list[int] = list()
        self.locked_cells: set[tuple[int, int]] = set()
        self.terminal_cells: set[tuple[int, int]] = set()
        self.terminal = terminal
        self._fitness = None

        # Pre-gravity checks
        for x, y in self.moves:
            self.state[x][y], self.state[x + 1][y] = self.state[x + 1][y], self.state[x][y]
            self.simulate_combo(lock_cells=True)
        self.lock_gravity_affected_cells()

        # Post-gravity checks
        self.simulate_gravity()
        if self.simulate_combo():
            self.chain += 1
        else:
            self.chain = 1

    def __lt__(self, other: 'GameState'):
        return (0 - self.fitness) < (0 - other._fitness)

    def simulate_combo(self, lock_cells: bool = False) -> bool:
        combo = set()
        for row in range(self.BOARD_HEIGHT - 2):
            for col in range(self.BOARD_WIDTH):
                color = self.state[col][row]
                if color and color == self.state[col][row + 1] == self.state[col][row + 2]:
                    combo.update((col, row + i) for i in range(3))
        for col in range(self.BOARD_WIDTH - 2):
            for row in range(self.BOARD_HEIGHT):
                color = self.state[col][row]
                if color and color == self.state[col + 1][row] == self.state[col + 2][row]:
                    combo.update((col + i, row) for i in range(3))

        combo_len = len(combo)
        if combo_len > 0:
            for cell in combo:
                if lock_cells:
                    self.locked_cells.add(cell)
                self.state[cell[0]][cell[1]] = 0
            self.combos.append(combo_len)
            self.chain = 1
        return combo_len != 0

    def simulate_gravity(self):
        for col in range(self.BOARD_WIDTH):
            if 0 in self.state[col]:
                stripped_col = [cell for cell in self.state[col] if cell]
                stripped_col += [0] * (self.BOARD_HEIGHT - len(stripped_col))
                self.state[col] = stripped_col

    def lock_gravity_affected_cells(self):
        for col in range(self.BOARD_WIDTH):
            zero_count = 0
            gravity_locked, gravity_terminal = set(), set()
            for row in range(self.BOARD_HEIGHT):
                if (col, row) in self.locked_cells:
                    zero_count = 0
                    continue
                if self.state[col][row]:
                    if zero_count:
                        gravity_terminal.update((col, r) for r in range(row - zero_count, row + 1))
                        gravity_locked.update((col, r) for r in range(row - 1, row + 1))
                else:
                    zero_count += 1
            self.locked_cells.update(gravity_locked)
            terminal_cells = gravity_terminal.difference(gravity_locked)
            if len(self.moves) == 1:
                self.terminal_cells.update(terminal_cells)
            else:
                self.locked_cells.update(terminal_cells)

    def get_height_metrics(self) -> tuple[int, int]:
        col_heights = []
        for c in range(self.BOARD_WIDTH):
            for r in range(self.BOARD_HEIGHT):
                if self.state[c][r] != 0: continue
                col_heights.append(r)
                break
        return max(col_heights), sum(abs(a - b) for a, b in zip(col_heights, col_heights[1:]))

    def get_metrics(self) -> list[int]:
        tallest, roughness = self.get_height_metrics()
        padded_combos = self.combos[:10]
        padded_combos += [0] * (10 - len(padded_combos))
        return padded_combos + [self.chain] + [tallest] + [roughness] + [self.get_move_count()]

    def get_move_count(self) -> int:
        moves = [self.initial_cursor] + self.moves
        move_count = 0
        for i in range(1, len(moves)):
            move_count += abs(moves[i][0] - moves[i - 1][0]) + abs(moves[i][1] - moves[i - 1][1]) + 1
        return move_count

    def print_board(self):
        print(''.center(11, '-'))
        for row in range(self.BOARD_HEIGHT - 1, -1, -1):
            for col in range(self.BOARD_WIDTH):
                print(self.state[col][row], end=" ")
            print()
        print(''.center(11, '-'))

    @property
    def fitness(self) -> float:
        if self._fitness: return self._fitness
        self._fitness = self.evaluator.get_fitness(self.get_metrics())
        return self._fitness

    def get_valid_children(self) -> list['GameState']:
        if self.terminal: return []
        valid = [m for m in self.MOVE_OPTIONS if m not in self.locked_cells
                 and (m[0] + 1, m[1]) not in self.locked_cells and self.state[m[0]][m[1]] != self.state[m[0] + 1][m[1]]]
        return [GameState(self.evaluator, self, m, terminal=(m in self.terminal_cells)) for m in valid]

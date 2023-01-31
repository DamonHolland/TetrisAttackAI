import time
import ctypes

import pydirectinput
import pymem
import pyautogui


def pause_fix(_pause):
    if _pause:
        nanosleep(50000000)


pydirectinput._handlePause = pause_fix


def nanosleep(nanoseconds):
    start_time = time.perf_counter_ns()
    end_time = start_time + nanoseconds
    while time.perf_counter_ns() < end_time:
        pass
    return True


class Game:
    PROCESS_NAME = 'bsnes.exe'
    LEFT_KEY = 'left'
    UP_KEY = 'up'
    RIGHT_KEY = 'right'
    DOWN_KEY = 'down'
    RAISE_KEY = 's'
    PRESS_KEY = 'v'
    RESET_KEY = 'f1'
    ALL_KEYS = [LEFT_KEY, UP_KEY, RIGHT_KEY, DOWN_KEY, RAISE_KEY, RESET_KEY]

    def __init__(self):
        self.snes_process = pymem.Pymem(self.PROCESS_NAME)
        self.base_addr = pymem.process.module_from_name(self.snes_process.process_handle, self.PROCESS_NAME).lpBaseOfDll

        self.score_addr = self.base_addr + 0x74F09E
        self.cursor_x_addr = self.base_addr + 0x74F180
        self.cursor_y_addr = self.base_addr + 0x74F184
        self.state_addr = self.base_addr + 0x74FE44
        self.live_addr = self.base_addr + 0x74F15C
        self.chain_addr = self.base_addr + 0x74F268

        self.game_window = pyautogui.getWindowsWithTitle("Tetris Attack")[0]
        self.game_window.activate()
        self.release_all_keys()

    def get_score(self) -> int:
        return self.snes_process.read_int(self.score_addr)

    def get_cursor_x(self) -> int:
        return int.from_bytes(self.snes_process.read_bytes(self.cursor_x_addr, 1), 'little') - 1

    def get_cursor_y(self) -> int:
        return abs(int.from_bytes(self.snes_process.read_bytes(self.cursor_y_addr, 1), 'little') - 14)

    def is_game_live(self) -> bool:
        return bool.from_bytes(self.snes_process.read_bytes(self.live_addr, 1), 'little')

    def get_tile_map(self) -> list[list[int]]:
        tile_map = []
        curr_addr = self.state_addr
        for row in range(12):
            game_row = []
            for col in range(6):
                game_row.append((int.from_bytes(self.snes_process.read_bytes(curr_addr, 1), "little")))
                curr_addr -= 2
            tile_map.append(list(reversed(game_row)))
            curr_addr -= 4
        return tile_map

    def get_chain(self) -> int:
        return int.from_bytes(self.snes_process.read_bytes(self.chain_addr, 1), 'little') + 1

    def perform_moves(self, moves: list[tuple[int, int]]):
        starting_cursor_x, starting_cursor_y = self.get_cursor_x(), self.get_cursor_y()
        if not self.game_window.isActive:
            self.game_window.activate()

        for cell_x, cell_y in moves:
            cursor_diff_x, cursor_diff_y = starting_cursor_x - cell_x, starting_cursor_y - cell_y
            print(f"Performing move {[cell_x, cell_y]}")
            for _ in range(abs(cursor_diff_x)):
                if cursor_diff_x > 0:
                    pydirectinput.press(self.LEFT_KEY)
                else:
                    pydirectinput.press(self.RIGHT_KEY)
            for _ in range(abs(cursor_diff_y)):
                if cursor_diff_y > 0:
                    pydirectinput.press(self.DOWN_KEY)
                else:
                    pydirectinput.press(self.UP_KEY)
            pydirectinput.press(self.PRESS_KEY)
            starting_cursor_x -= cursor_diff_x
            starting_cursor_y -= cursor_diff_y

    def restart_game(self):
        if not self.game_window.isActive:
            self.game_window.activate()
        pydirectinput.press(self.RESET_KEY)
        while True:
            if self.is_game_live():
                return

    def perform_raise(self):
        pydirectinput.press(self.RAISE_KEY)

    def release_all_keys(self):
        [ctypes.windll.user32.keybd_event(key, 0, 2, 0) for key in self.ALL_KEYS]

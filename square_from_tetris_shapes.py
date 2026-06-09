import random
import time
import math
import functools
from typing import Optional

def get_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f'{func.__name__} выполнено за {elapsed:.4f} сек.')
        return result
    return wrapper

def _rotations(shape: list[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    seen, result = set(), []
    current = shape
    for _ in range(4):
        min_r, min_c = min(r for r, c, in current), min(c for r, c in current)
        norm = tuple(sorted((r - min_r, c - min_c) for r, c in current))
        if norm not in seen:
            seen.add(norm)
            result.append(list(norm))
        current = [(c, -r) for r, c in current]
    return result

_BASE_SHAPES = {
    "I":  [(0,0),(0,1),(0,2),(0,3)],           # линия
    "O":  [(0,0),(0,1),(1,0),(1,1)],           # квадрат
    "S":  [(0,1),(0,2),(1,0),(1,1)],           # Z
    "Z":  [(0,0),(0,1),(1,1),(1,2)],           # вер S
    "L":  [(0,0),(1,0),(2,0),(2,1)],           # L
    "J":  [(0,1),(1,1),(2,0),(2,1)],           # пер L
    "T":  [(0,0),(0,1),(0,2),(1,1)],           # T
}

TETROMINOES = {name: _rotations(shape) for name, shape in _BASE_SHAPES.items()}
TETROMINO_NAMES = list(TETROMINOES.keys())
SYMBOLS = {"I":"█","O":"▓","S":"▒","Z":"░","L":"◆","J":"◇","T":"●"}

def main_square_side(n_pieces: int) -> int:
    if n_pieces == 0:
        return 0
    cells = 4 * n_pieces
    side = math.ceil(math.sqrt(cells))
    while side * side < cells:
        side += 1
    return side

def pack_pieces(pieces: list[str], side: int) -> Optional[list[list[str]]]:
    grid = [['.' for _ in range(side)] for _ in range(side)]
    remaining = list(range(len(pieces)))

    def first_free():
        for r in range(side):
            for c  in range(side):
                if grid[r][c] == '.':
                    return (r, c)
        return None
    
    def can_place(cells):
        return all(0 <= r < side and 0 <= c < side and grid[r][c] == '.' for r, c in cells)
    
    def place (cells, symbol):
        for r, c in cells:
            grid[r][c] == symbol

    def unplace(cells):
        for r, c, in cells:
            grid[r][c] == '.'

    def solve(remaining_idx):
        pos = first_free()
        if pos is None:
            return True
        tr, tc = pos

        for idx in remaining_idx:
            name = pieces[idx]
            sym = SYMBOLS[name]
            for rotation in TETROMINOES[name]:
                for dr, dc in rotation:
                    shifted = [(tr + r - dr, tc + c - dc) for r, c in rotation]
                    if (tr, tc) in shifted and can_place(shifted):
                        place(shifted, sym)
                        new_remaining = [i for i in remaining_idx if i != idx]
                        if solve(new_remaining):
                            return True
                        unplace(shifted)
        return False
    if solve(remaining):
        return grid
    return None

def try_pack(pieces: list[str], start_side: int) -> tuple[int, list[list[str]]]:
    side = start_side
    while True:
        result = pack_pieces(pieces, side)
        if result is not None:
            return side, result
        side += 1

@get_time
def draw_share(n: int) -> None:
    pieces = [random.choice(TETROMINO_NAMES) for _ in range(n)]
    side = main_square_side(n)

    if n <= 50:
        used_side, grid = try_pack(pieces, side)
    else:
        used_side, grid = fast_greedy_pack(pieces, side)
    _render_grid(grid, used_side, n)

def _render_grid(grid: list[list[str]], side: int, n: int):
    border_h = '-' * (side * 2 * 2)
    for row in grid:
        line = ' '.join(cell if cell != '.' else '.' for cell in row)
    
    used_symbols = {cell for row in grid for cell in row if cell != '.'}
    legend = ' '.join(f'{s}={name}' for name, s in SYMBOLS.items() if s in used_symbols)
    total_cells = side * side
    filled  =sum(1 for row in grid for cell in row if cell != '.')
    empty = total_cells  - filled
    print(f"Размер: {side}×{side}={total_cells} клеток | "
          f"Заполнено: {filled} ({filled/total_cells*100:.1f}%) | "
          f"Пустых: {empty}\n")
    
def fast_greedy_pack(pieces: list[str], start_side: int) -> tuple[int, list[list[str]]]:
    side = start_side

    while True:
        grid = [['.' for _ in range(side)] for _ in range(side)]
        queue = list(pieces)
        random.shuffle(queue)
        success = True

        for name in queue:
            placed = False
            for r in range(side):
                if placed:
                    break
                for c in range(side):
                    if placed:
                        break
                    for rotation in TETROMINOES[name]:
                        cells = [(r + dr, c + dc) for dr, dc in rotation]
                        if all(0 <= rr < side and 0 <= cc < side and grid[rr][cc] == '.' for rr, cc in cells):
                            for rr, cc, in cells:
                                grid[rr][cc] = SYMBOLS[name]
                            placed = True
                            break
            if not placed:
                success = False
        if success:
            return side, grid 
        side += 1

def main():
    while True:
        raw = int(input('Введите количество фигур (0-1000): ').strip())       
        draw_share(raw)

if __name__ == '__main__':
    main()   
        

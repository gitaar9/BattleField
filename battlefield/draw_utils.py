from game_constants import GRID_ROWS


def calculate_perspective_factor(y):
    return 1 - (y / GRID_ROWS) * 0.35

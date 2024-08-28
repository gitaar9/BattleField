import random

import numpy as np

from ai_character import AICharacter
from game_constants import GRID_ROWS, CELL_SIZE, MOVEMENT_DELAY, \
    GRID_COLUMNS
from player_character import PlayerCharacter
from trees import Tree1, Tree2


class GameState:
    def __init__(self):
        self.player_character = PlayerCharacter(5, GRID_ROWS // 2, CELL_SIZE, MOVEMENT_DELAY)
        self.ai_characters = [
            AICharacter(
                position_x=20,
                position_y=2,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY
            ),
            AICharacter(
                position_x=20,
                position_y=5,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY
            ),
            AICharacter(
                position_x=20,
                position_y=8,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY
            ),
        ]

        # Init some random trees
        self.trees = []
        self.stuff = []
        self.setup_field()

    @property
    def drawables(self):
        return [self.player_character] + self.trees + self.stuff + self.ai_characters

    @property
    def walkable_tiles(self) -> np.ndarray:
        grid = np.ones((GRID_ROWS, GRID_COLUMNS), bool)
        for d in self.drawables:
            grid[d.grid_y, d.grid_x] = False
        return grid

    def setup_field(self):
        # Create border trees
        left_coords = [(4, 0), (4, 1), (3, 2), (3, 3), (2, 4), (2, 5), (1, 6), (1, 7), (0, 8), (0, 9)]
        for x, y in left_coords:
            for loop_x in range(0, x + 1):
                self.trees.append(Tree1(loop_x, y))

        right_coords = [(25, 0), (25, 1), (26, 2), (26, 3), (27, 4), (27, 5), (28, 6), (28, 7), (29, 8), (29, 9)]
        for x, y in right_coords:
            for loop_x in range(x, GRID_COLUMNS):
                self.trees.append(Tree1(loop_x, y))

        # Add random trees
        for _ in range(7):
            self.trees.append(Tree1(*self.random_empty_coordinates()))
        for _ in range(5):
            self.trees.append(Tree2(*self.random_empty_coordinates()))

        self.trees = sorted(self.trees, key=lambda t: t.grid_y, reverse=True)

    def random_empty_coordinates(self):
        empty_spots = self.walkable_tiles
        x, y = random.randint(0, GRID_COLUMNS - 1), random.randint(0, GRID_ROWS - 1)
        while not empty_spots[y, x]:
            x, y = random.randint(0, GRID_COLUMNS - 1), random.randint(0, GRID_ROWS - 1)
        return x, y


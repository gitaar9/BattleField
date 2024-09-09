import random

import numpy as np

from ai_character import AICharacter, AIKnight
from ai_archer import AIArcher
from game_constants import GRID_ROWS, CELL_SIZE, MOVEMENT_DELAY, \
    GRID_COLUMNS
from player_character import PlayerCharacter
from trees import Tree1, Tree2
from weapon import Arrow


class GameState:
    def __init__(self):
        self.player_character = PlayerCharacter(5, GRID_ROWS // 2 - 1, CELL_SIZE, MOVEMENT_DELAY, team=0)
        # self.ai_characters = [
        #     AIArcher(
        #         position_x=20,
        #         position_y=2,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=0
        #     ),
        #     AIArcher(
        #         position_x=20,
        #         position_y=5,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AIArcher(
        #         position_x=20,
        #         position_y=8,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AIArcher(
        #         position_x=22,
        #         position_y=1,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AIArcher(
        #         position_x=22,
        #         position_y=4,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AIArcher(
        #         position_x=22,
        #         position_y=7,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AICharacter(
        #         position_x=18,
        #         position_y=2,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AICharacter(
        #         position_x=18,
        #         position_y=5,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AICharacter(
        #         position_x=18,
        #         position_y=8,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AICharacter(
        #         position_x=18,
        #         position_y=1,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AICharacter(
        #         position_x=18,
        #         position_y=4,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        #     AICharacter(
        #         position_x=18,
        #         position_y=7,
        #         cell_size=CELL_SIZE,
        #         move_delay=MOVEMENT_DELAY,
        #         team=1
        #     ),
        # ]

        self.ai_characters = [
            AICharacter(
                position_x=18,
                position_y=2,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            ),
            AICharacter(
                position_x=18,
                position_y=5,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            ),
            AICharacter(
                position_x=18,
                position_y=8,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            ),
            AICharacter(
                position_x=20,
                position_y=2,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            ),
            AICharacter(
                position_x=20,
                position_y=5,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            ),
            AICharacter(
                position_x=20,
                position_y=8,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            ),
            AICharacter(
                position_x=5,
                position_y=1,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=0
            ),
            AICharacter(
                position_x=5,
                position_y=4,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=0
            ),
            AICharacter(
                position_x=5,
                position_y=7,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=0
            ),
            AICharacter(
                position_x=5,
                position_y=6,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=0
            ),
            AICharacter(
                position_x=5,
                position_y=8,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=0
            ),
            AIArcher(
                position_x=18,
                position_y=7,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            ),
            AIKnight(
                position_x=21,
                position_y=8,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            ),
        ]
        self.ai_characters = [
            AIArcher(
                position_x=18,
                position_y=7,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            ),
        ]

        # Init some random trees
        self.trees = []
        self.arrows = [
            Arrow(
                position_x=22,
                position_y=6,
                velocity_x=-4,
                velocity_y=0,
                cell_size=CELL_SIZE,
            )
        ]
        self.stuff = []
        self.setup_field()
        self.grid = None
        self.update_game_grid()

    @property
    def drawables(self):
        return self.trees + self.stuff + self.characters + self.arrows

    @property
    def characters(self):
        return [self.player_character] + self.ai_characters

    @property
    def walkable_tiles(self) -> np.ndarray:
        grid = np.ones((GRID_ROWS, GRID_COLUMNS), bool)
        for d in self.drawables:
            from hitpoints_mixin import HitPointsMixin
            if isinstance(d, HitPointsMixin):
                if not d.is_dead():
                    grid[d.grid_y, d.grid_x] = False
            else:
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
        num_random_trees = 14
        for _ in range(num_random_trees // 3 * 2):
            self.trees.append(Tree1(*self.random_empty_coordinates()))
        for _ in range(num_random_trees // 3):
            self.trees.append(Tree2(*self.random_empty_coordinates()))

        self.trees = sorted(self.trees, key=lambda t: t.grid_y, reverse=True)

    def random_empty_coordinates(self):
        empty_spots = self.walkable_tiles
        x, y = random.randint(0, GRID_COLUMNS - 1), random.randint(0, GRID_ROWS - 1)
        while not empty_spots[y, x]:
            x, y = random.randint(0, GRID_COLUMNS - 1), random.randint(0, GRID_ROWS - 1)
        return x, y

    def update_game_grid(self):
        """ Create a grid representing the current state of all elements on the field. Index with [y][x]"""
        # Initialize an empty grid
        self.grid = [[None for _ in range(GRID_COLUMNS)] for _ in range(GRID_ROWS)]

        # Place trees
        for tree in self.trees:
            self.grid[tree.grid_y][tree.grid_x] = tree

        # Place AI characters
        for character in self.characters:
            if not character.is_dead():
                self.grid[character.grid_y][character.grid_x] = character

        # Place the player character
        # self.grid[self.player_character.grid_y][self.player_character.grid_x] = self.player_character

    @property
    def game_grid(self):
        return self.grid
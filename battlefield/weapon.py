import time

import arcade

from draw_utils import calculate_perspective_factor
from game_constants import GRID_ROWS, GRID_COLUMNS, MOVEMENT_DELAY, SCREEN_WIDTH, BOTTOM_GRID_PAD, HORIZONTAL_PADDING, \
    CELL_SIZE


class Weapon:
    def __init__(self, damage, frame_time, move_delay_time):
        self.damage = damage
        self.frame_time = frame_time
        self.move_delay_time = move_delay_time
        self.hit_cooldown_time = 10
        self.hit_cooldown = self.hit_cooldown_time

    def update(self):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def reset_hit_cooldown(self):
        self.hit_cooldown = self.hit_cooldown_time

    def get_targets_in_range(self, user, game_state):
        if user.facing_left:
            if user.grid_x - 1 > 0:
                return [game_state.game_grid[user.grid_y][user.grid_x - 1]]
        else:
            if user.grid_x + 1 < GRID_COLUMNS:
                return [game_state.game_grid[user.grid_y][user.grid_x + 1]]
        return []

    def attack(self, user, game_state):
        if self.hit_cooldown == 0:
            self.reset_hit_cooldown()
            targets = self.get_targets_in_range(user, game_state)
            for target in targets:
                if target is not None and target.team != user.team:
                    target.hit(self.damage)


class Bow(Weapon):
    def attack(self, user, game_state):
        if self.hit_cooldown == 0:
            self.reset_hit_cooldown()
            arrow_velocity = 4 * (-1 if user.facing_left else 1)
            game_state.arrows.append(Arrow(position_x=user.grid_x, position_y=user.grid_y, velocity_x=arrow_velocity, velocity_y=0, cell_size=CELL_SIZE))


class Arrow:
    def __init__(self, position_x, position_y, velocity_x, velocity_y, cell_size):
        # Initialize grid and screen positions
        self.grid_x = position_x
        self.grid_y = position_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.cell_size = cell_size
        self.screen_x, self.screen_y = self.calculate_screen_position(self.grid_x, self.grid_y)

        self.last_move_time = time.time()

    def calculate_screen_position(self, grid_x, grid_y):
        """ Calculate the on-screen position of the character based on grid coordinates. """
        perspective_factor = calculate_perspective_factor(self.grid_y)
        cell_width = self.cell_size * perspective_factor
        cell_height = self.cell_size * perspective_factor

        screen_x = grid_x * cell_width + (SCREEN_WIDTH / 2) - (GRID_COLUMNS * cell_width / 2)
        screen_y = grid_y * cell_height + BOTTOM_GRID_PAD + HORIZONTAL_PADDING * grid_y

        return screen_x, screen_y

    def calculate_grid_position(self):
        """ Calculate the grid position of the character based on screen coordinates. """
        perspective_factor = calculate_perspective_factor(self.grid_y)  # Use self.grid_y for the perspective factor
        cell_width = self.cell_size * perspective_factor
        cell_height = self.cell_size * perspective_factor

        # Reverse the screen_x and screen_y calculations
        grid_x = ((self.screen_x + cell_width / 2) - (SCREEN_WIDTH / 2) + (GRID_COLUMNS * cell_width / 2)) / cell_width
        grid_y = (self.screen_y - BOTTOM_GRID_PAD - HORIZONTAL_PADDING * self.grid_y) / cell_height

        return max(0, min(int(grid_x), GRID_COLUMNS - 1)), max(0, min(int(grid_y), GRID_ROWS -1))

    def draw(self):
        """ Draw the arrow on the screen. """
        perspective_factor = calculate_perspective_factor(self.grid_y)  # Use self.grid_y for the perspective factor
        cell_width = self.cell_size * perspective_factor
        cell_height = self.cell_size * perspective_factor

        y = self.screen_y + cell_height * .85
        arcade.draw_line(self.screen_x, y, self.screen_x + (10 * calculate_perspective_factor(self.grid_y)), y, arcade.color.BROWN, 2)

    def update(self, delta_time):
        """ Update the arrow's screen position based on velocity and update grid position accordingly. """
        # Move the arrow based on its velocity
        self.screen_x += self.velocity_x
        self.screen_y += self.velocity_y

        # Update the grid position based on the new screen position
        self.grid_x, self.grid_y = self.calculate_grid_position()

        # Check if arrow goes outside the grid
        if self.grid_x < 0 or self.grid_x >= GRID_COLUMNS or self.grid_y < 0 or self.grid_y >= GRID_ROWS:
            return False  # Arrow is outside the grid
        return True  # Arrow is still within the grid

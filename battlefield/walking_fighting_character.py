import time
import arcade

from animation import Animation
from draw_utils import calculate_perspective_factor
from game_constants import BOTTOM_GRID_PAD, HORIZONTAL_PADDING, SCREEN_WIDTH, GRID_ROWS, GRID_COLUMNS, \
    STANDARD_FRAME_TIME


class WalkingFightingCharacter:
    def __init__(self, position_x, position_y, cell_size, move_delay):
        self.cell_size = cell_size
        self.move_delay = move_delay
        self.grid_x = position_x
        self.grid_y = position_y
        self.screen_x, self.screen_y = self.calculate_screen_position(position_x, position_y)
        self.target_x = self.screen_x
        self.target_y = self.screen_y
        self.x_screen_distance = None
        self.y_screen_distance = None
        self.screen_x_prev = None
        self.screen_y_prev = None
        self.cell_size_factor = 1.7
        self.bottom_padding = 10

        self.last_move_time = time.time()
        self.facing_left = True
        self.fighting = False

        self.animations = {
            'facing_left': Animation("resources/main_character/walk_left.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'facing_right': Animation("resources/main_character/walk_right.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
            'fighting_left': Animation("resources/main_character/attacks_left.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=-9),
            'fighting_right': Animation("resources/main_character/attack_right.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=9),
        }

    def calculate_screen_position(self, grid_x, grid_y):
        """ Calculate the on-screen position of the character based on grid coordinates. """
        perspective_factor = calculate_perspective_factor(self.grid_y)
        cell_width = self.cell_size * perspective_factor
        cell_height = self.cell_size * perspective_factor

        screen_x = grid_x * cell_width + (SCREEN_WIDTH / 2) - (GRID_COLUMNS * cell_width / 2)
        screen_y = grid_y * cell_height + BOTTOM_GRID_PAD + HORIZONTAL_PADDING * grid_y

        return screen_x, screen_y

    def draw(self):
        """ Draw the player character as a rectangle on the grid. """
        perspective_factor = calculate_perspective_factor(self.grid_y)
        cell_width = self.cell_size * perspective_factor

        animation = self.get_current_animation()
        animation.scale = (cell_width * self.cell_size_factor / animation.frame_width)
        animation.draw(
            center_x=self.screen_x + (animation.frame_width * animation.scale) / 2 - (self.cell_size * (self.cell_size_factor - 1) / 2),
            center_y=self.screen_y + (animation.frame_height * animation.scale) / 2 + self.bottom_padding * perspective_factor,
            perspective_factor=perspective_factor
        )

    def get_current_animation(self):
        if self.fighting:
            return self.animations['fighting_left'] if self.facing_left else self.animations['fighting_right']
        else:
            return self.animations['facing_left'] if self.facing_left else self.animations['facing_right']

    def update_animation(self):
        # Update the animation based on movement
        self.get_current_animation().update()

        if (time.time() - self.last_move_time) >= self.move_delay:
            if self.fighting:
                self.animations['facing_left'].set_animation_phase(self.animations['fighting_left'].get_animation_phase())
                self.animations['facing_left'].playing = False
                self.animations['facing_right'].set_animation_phase(self.animations['fighting_right'].get_animation_phase())
                self.animations['facing_right'].playing = False
            else:
                self.animations['fighting_left'].set_animation_phase(self.animations['facing_left'].get_animation_phase())
                self.animations['fighting_right'].set_animation_phase(self.animations['facing_right'].get_animation_phase())

    def handle_player_input(self, game_state, keys_pressed, walkable_tiles):
        pass

    def handle_ai_planning(self, game_state, keys_pressed, walkable_tiles):
        pass

    def update(self, delta_time, game_state, keys_pressed, walkable_tiles):
        """ Update the position of the character smoothly based on keys pressed. """

        self.update_animation()

        if (time.time() - self.last_move_time) >= self.move_delay:
            self.fighting = False
            self.screen_x = self.target_x
            self.screen_y = self.target_y

        # Make sure player controlled and AI controlled characters move
        self.handle_player_input(game_state, keys_pressed, walkable_tiles)
        self.handle_ai_planning(game_state, keys_pressed, walkable_tiles)

        # Linear interpolation
        if self.screen_x != self.target_x or self.screen_y != self.target_y:
            elapsed_time = time.time() - self.last_move_time
            total_time = self.move_delay
            factor = min(1, elapsed_time / total_time)
            self.screen_x = self.screen_x_prev + self.x_screen_distance * factor
            self.screen_y = self.screen_y_prev + self.y_screen_distance * factor

    def fight(self):
        if self.facing_left:
            self.animations['fighting_left'].reset()
        else:
            self.animations['fighting_right'].reset()
        self.fighting = True
        self.set_last_move_time()

    def set_last_move_time(self):
        self.last_move_time = time.time()

    @property
    def move_delay_active(self):
        return (time.time() - self.last_move_time) < self.move_delay

    def move(self, delta_x, delta_y, walkable_tiles):
        """ Initiate movement to a new grid position. """
        if delta_x > 0:
            self.facing_left = False
        if delta_x < 0:
            self.facing_left = True

        new_x = self.grid_x + delta_x
        new_y = self.grid_y + delta_y

        # Figure out if we can move there
        if new_x < 0 or new_x > GRID_COLUMNS - 1:
            return
        if new_y < 0 or new_y > GRID_ROWS - 1:
            return
        if not walkable_tiles[new_y, new_x]:
            return

        if self.facing_left:
            self.animations['facing_left'].reset()
        else:
            self.animations['facing_right'].reset()

        self.grid_x = new_x
        self.grid_y = new_y

        self.target_x, self.target_y = self.calculate_screen_position(self.grid_x, self.grid_y)

        self.screen_x_prev = self.screen_x
        self.screen_y_prev = self.screen_y

        self.x_screen_distance = self.target_x - self.screen_x
        self.y_screen_distance = self.target_y - self.screen_y
        self.set_last_move_time()

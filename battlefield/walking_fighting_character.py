import time
import arcade

from animation import Animation
from draw_utils import calculate_perspective_factor
from game_constants import BOTTOM_GRID_PAD, HORIZONTAL_PADDING, SCREEN_WIDTH, GRID_ROWS, GRID_COLUMNS, \
    STANDARD_FRAME_TIME, MOVEMENT_DELAY
from hitpoints_mixin import HitPointsMixin
from weapon import Weapon


class WalkingFightingCharacter(HitPointsMixin):
    def __init__(self, position_x, position_y, cell_size, move_delay, team=0):
        HitPointsMixin.__init__(self, hp=100)
        self.cell_size = cell_size
        self.move_delay = move_delay
        self.grid_x: int = position_x
        self.grid_y: int = position_y
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
        self.team = team

        self.weapon = Weapon(10, STANDARD_FRAME_TIME / 2, MOVEMENT_DELAY)

        self.animations = {
            'facing_left': Animation("resources/main_character/walk_left.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'facing_right': Animation("resources/main_character/walk_right.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
            'fighting_left': Animation("resources/main_character/attacks_left.png", 48, 48, 8, 16, frame_duration=self.weapon.frame_time, scale=1.0, loop=False, margin_x=-9),
            'fighting_right': Animation("resources/main_character/attack_right.png", 48, 48, 8, 16, frame_duration=self.weapon.frame_time, scale=1.0, loop=False, margin_x=9),
            'death_left': Animation("resources/farmer_character/death_left.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'death_right': Animation("resources/farmer_character/death_right.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
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
        """ Draw the player character and their HP bar on the grid. """
        perspective_factor = calculate_perspective_factor(self.grid_y)
        cell_width = self.cell_size * perspective_factor
        animation = self.get_current_animation()
        animation.scale = (cell_width * self.cell_size_factor / animation.frame_width) + 0.015 * self.hit_cooldown
        center_x = self.screen_x + (animation.frame_width * animation.scale) / 2 - (
                    self.cell_size * (self.cell_size_factor - 1) / 2)
        center_y = self.screen_y + (
                    animation.frame_height * animation.scale) / 2 + self.bottom_padding * perspective_factor

        # Draw team indication
        if not self.is_dead():
            ellipse_width = cell_width * 0.7
            ellipse_height = cell_width * 0.3
            team_color = arcade.color.RED if self.team == 1 else arcade.color.BLUE  # Change colors based on team
            arcade.draw_ellipse_filled(
                center_x + (-cell_width*0.1 if self.facing_left else cell_width*0.1),
                center_y - animation.frame_height * animation.scale / 2,
                ellipse_width,
                ellipse_height,
                (*team_color, 64)
            )  # Half transparency

        # Drawing the character
        animation.draw(center_x=center_x, center_y=center_y, perspective_factor=perspective_factor)

        # Constants for the HP bar
        if not self.is_dead():
            self.draw_hp_bar(
                center_x=center_x,
                center_y=center_y + (animation.frame_height * animation.scale * 0.4),
                hp_bar_width=(cell_width * .9) * perspective_factor
            )

    def get_current_animation(self):
        if self.is_dead():
            return self.animations['death_left'] if self.facing_left else self.animations['death_right']
        if self.fighting:
            return self.animations['fighting_left'] if self.facing_left else self.animations['fighting_right']
        else:
            return self.animations['facing_left'] if self.facing_left else self.animations['facing_right']

    def update_animation(self):
        # Update the animation based on movement
        self.get_current_animation().update()

        if not self.is_dead() and (time.time() - self.last_move_time) >= self.move_delay:
            if self.fighting:
                self.animations['facing_left'].set_animation_phase(self.animations['fighting_left'].get_animation_phase())
                self.animations['facing_left'].playing = False
                self.animations['facing_right'].set_animation_phase(self.animations['fighting_right'].get_animation_phase())
                self.animations['facing_right'].playing = False
            else:
                self.animations['fighting_left'].set_animation_phase(self.animations['facing_left'].get_animation_phase())
                self.animations['fighting_right'].set_animation_phase(self.animations['facing_right'].get_animation_phase())
            self.animations['death_left'].set_animation_phase(self.animations['fighting_left'].get_animation_phase())
            self.animations['death_left'].reset()
            self.animations['death_right'].set_animation_phase(self.animations['fighting_right'].get_animation_phase())
            self.animations['death_right'].reset()

    def handle_player_input(self, game_state, keys_pressed):
        pass

    def handle_ai_planning(self, game_state, keys_pressed):
        pass

    def get_potential_hit_target(self, game_state):
        if self.facing_left:
            if self.grid_x - 1 > 0:
                return game_state.game_grid[self.grid_y][self.grid_x - 1]
        else:
            if self.grid_x + 1 < GRID_COLUMNS:
                return game_state.game_grid[self.grid_y][self.grid_x + 1]
        return None

    def update(self, delta_time, game_state, keys_pressed):
        """ Update the position of the character smoothly based on keys pressed. """
        if self.is_dead():
            self.update_animation()
            return
        super().update()

        # Weapon stuff
        self.weapon.update()
        if self.fighting and self.get_current_animation().is_in_hit_frame():
            # potential_target = self.get_potential_hit_target(game_state)
            # if potential_target is not None and isinstance(potential_target, WalkingFightingCharacter):
            self.weapon.attack(self, game_state)
        self.update_animation()

        if (time.time() - self.last_move_time) >= self.move_delay:
            self.fighting = False
            self.screen_x = self.target_x
            self.screen_y = self.target_y

        # Make sure player controlled and AI controlled characters move
        self.handle_player_input(game_state, keys_pressed)
        self.handle_ai_planning(game_state, keys_pressed)

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
        self.set_last_move_time(self.weapon.move_delay_time)

    def set_last_move_time(self, new_move_delay_time=None):
        self.last_move_time = time.time()
        if new_move_delay_time is not None:
            self.move_delay = new_move_delay_time

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
            return False
        if new_y < 0 or new_y > GRID_ROWS - 1:
            return False
        if not walkable_tiles[new_y, new_x]:
            if delta_x != 0 and delta_y != 0:  # If both deltas are non-zero move in try to move in either direction
                if self.move(delta_x, 0, walkable_tiles):
                    return True
                return self.move(0, delta_y, walkable_tiles)
            return False

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
        self.set_last_move_time(MOVEMENT_DELAY)

        return True
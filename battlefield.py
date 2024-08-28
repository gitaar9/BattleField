import random
from copy import deepcopy
from tkinter.tix import Tree

import arcade
import time

import numpy as np
from PIL import ImageEnhance
from arcade import load_texture

# Constants for the game
BOTTOM_GRID_PAD = 30
HORIZONTAL_PADDING = 3
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Grid Battlefield"
GRID_ROWS = 10  # Number of rows
GRID_COLUMNS = 30  # Number of columns
CELL_SIZE = (SCREEN_WIDTH - BOTTOM_GRID_PAD * 2) / 20  # Size of the grid cell at the front

STANDARD_FRAME_TIME = 1 / 10
MOVEMENT_DELAY = STANDARD_FRAME_TIME * 4  # Delay in seconds for full movement to complete


def calculate_perspective_factor(y):
    return 1 - (y / GRID_ROWS) * 0.35


class StationarySprite:
    def __init__(self, position_x, position_y, cell_size, image_file, bottom_padding=1, cell_size_factor=1.3, random_placement_pixels=2, margin_x=0, random_horizontal_flip=False):
        self.grid_x = position_x
        self.grid_y = position_y
        self.cell_size = cell_size
        self.image_file = image_file
        self.margin_x = margin_x

        self.texture = load_texture(
                image_file,
                0,
                0,
                0,
                0,
                flipped_horizontally=random_horizontal_flip and random.random() > .5,
                flipped_vertically=False,
                flipped_diagonally=False,
                hit_box_algorithm="Simple",
                hit_box_detail=4.5,
                can_cache=False
            )

        # Brightness change only works for mirrored textures (all textures with same orientation have same brightness)
        enhancer = ImageEnhance.Brightness(deepcopy(self.texture.image))
        random_brightness_range = 0.4
        factor = random.random() * random_brightness_range + (1 - (random_brightness_range / 2))  # Darkens the image; 0.5 means 50% brightness.
        brightness_randomized_image = enhancer.enhance(factor)
        self.texture.image = brightness_randomized_image

        self.sprite = arcade.Sprite(texture=self.texture, scale=1.0)

        perspective_factor = calculate_perspective_factor(self.grid_y)
        cell_width = self.cell_size * perspective_factor
        cell_height = self.cell_size * perspective_factor
        self.screen_x = self.grid_x * cell_width + (SCREEN_WIDTH / 2) - (GRID_COLUMNS * cell_width / 2)
        self.screen_y = self.grid_y * cell_height + BOTTOM_GRID_PAD + HORIZONTAL_PADDING * self.grid_y

        self.screen_x += random.randrange(-random_placement_pixels, random_placement_pixels) * perspective_factor
        self.screen_y += random.randrange(-random_placement_pixels, random_placement_pixels) * perspective_factor

        self.sprite.scale = perspective_factor * (self.cell_size * cell_size_factor / self.sprite.width)
        self.sprite.center_x = self.screen_x + self.margin_x * self.sprite.scale + self.sprite.width / 2 - (self.cell_size * (cell_size_factor - 1) / 2)
        self.sprite.center_y = self.screen_y + self.sprite.height / 2 + bottom_padding * perspective_factor

    def draw(self):
        """ Draw the tree sprite on the grid. """
        self.sprite.draw()


class Tree1(StationarySprite):
    def __init__(self, position_x, position_y):
        super().__init__(
            position_x=position_x,
            position_y=position_y,
            cell_size=CELL_SIZE,
            image_file="resources/cutout_tree1.webp",
            bottom_padding=2,
            cell_size_factor=2,
            random_horizontal_flip=True
        )


class Tree2(StationarySprite):
    def __init__(self, position_x, position_y):
        super().__init__(
            position_x=position_x,
            position_y=position_y,
            cell_size=CELL_SIZE,
            image_file="resources/cutout_tree2.webp",
            bottom_padding=3,
            cell_size_factor=2,
            random_horizontal_flip=True
        )


class Animation:
    def __init__(self, file_path, frame_width, frame_height, columns, frame_count, frame_duration=0.05, scale=1.0, loop=True, margin_x=0):
        self.texture_list = arcade.load_spritesheet(file_path, frame_width, frame_height, columns, frame_count)
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.margin_x = margin_x
        self.frame_count = frame_count
        self.current_frame = 0
        self.scale = scale
        self.loop = loop
        self.playing = loop
        self.frame_duration = frame_duration  # Time in seconds for each frame
        self.last_update_time = time.time()
        self.animation_parts = 2

    def update(self):
        if not self.playing:
            return

        if time.time() - self.last_update_time > self.frame_duration:
            if self.loop:
                self.current_frame = (self.current_frame + 1) % self.frame_count
            else:
                self.current_frame = min(self.current_frame + 1, self.frame_count - 1)
                if self.current_frame == (self.frame_count // self.animation_parts) - 1:
                    self.playing = False
            self.last_update_time = time.time()

    def draw(self, center_x, center_y, perspective_factor=1):
        sprite = self.texture_list[self.current_frame]
        arcade.draw_texture_rectangle(center_x + self.margin_x * self.scale, center_y, sprite.width * self.scale, sprite.height * self.scale, sprite)

    def reset(self):
        if self.current_frame == self.frame_count - 1:
            self.current_frame = 0
        self.playing = True

    def get_animation_phase(self):
        return self.current_frame // (self.frame_count // self.animation_parts)

    def set_animation_phase(self, animation_phase):
        if animation_phase >= self.animation_parts:
            raise ValueError('Animation phase out of range')
        self.current_frame = (self.frame_count // self.animation_parts) * (animation_phase + 1) - 1


class PlayerCharacter:
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

        self.last_move_time = time.time()
        self.facing_left = True
        self.fighting = False

        self.sprites = {
            'facing_left': arcade.Sprite("resources/main_character1.webp", scale=1.0),
            'facing_right': arcade.Sprite("resources/main_character1.webp", scale=1.0, flipped_horizontally=True),
        }

        self.animations = {
            'facing_left': Animation("resources/character_walk_left.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'facing_right': Animation("resources/character_walk_right.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
            'fighting_left': Animation("resources/20240827_both_attacks_left.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=-9),
            'fighting_right': Animation("resources/20240827_both_attacks_right.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=9),
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
        # cell_height = self.cell_size * perspective_factor
        # arcade.draw_rectangle_filled(self.screen_x + cell_width / 2,
        #                              self.screen_y + cell_height / 2,
        #                              cell_width - 5, cell_height - 5, arcade.color.BLUE)
        cell_size_factor = 1.8
        bottom_padding = 10

        sprite = self.sprites['facing_left'] if self.facing_left else self.sprites['facing_right']
        sprite.scale = (cell_width * cell_size_factor / sprite.texture.width)
        sprite.center_x = self.screen_x + sprite.width / 2 - (self.cell_size * (cell_size_factor - 1) / 2)
        sprite.center_y = self.screen_y + sprite.height / 2 + bottom_padding * perspective_factor
        # sprite.draw()

        if self.fighting:
            animation = self.animations['fighting_left'] if self.facing_left else self.animations['fighting_right']
        else:
            animation = self.animations['facing_left'] if self.facing_left else self.animations['facing_right']
        animation.scale = (cell_width * cell_size_factor / animation.frame_width)
        animation.draw(
            center_x=self.screen_x + (animation.frame_width * animation.scale) / 2 - (self.cell_size * (cell_size_factor - 1) / 2),
            center_y=self.screen_y + (animation.frame_height * animation.scale) / 2 + bottom_padding * perspective_factor,
            perspective_factor=perspective_factor
        )

    def update(self, delta_time, keys_pressed, walkable_tiles):
        """ Update the position of the character smoothly based on keys pressed. """
        # Update the animation based on movement
        if self.fighting:
            animation = self.animations['fighting_left'] if self.facing_left else self.animations['fighting_right']
        else:
            animation = self.animations['facing_left'] if self.facing_left else self.animations['facing_right']
        animation.update()

        if (time.time() - self.last_move_time >= self.move_delay):
            if self.fighting:
                self.fighting = False
                self.animations['facing_left'].set_animation_phase(self.animations['fighting_left'].get_animation_phase())
                self.animations['facing_left'].playing = False
                self.animations['facing_right'].set_animation_phase(self.animations['fighting_right'].get_animation_phase())
                self.animations['facing_right'].playing = False
            else:
                self.animations['fighting_left'].set_animation_phase(self.animations['facing_left'].get_animation_phase())
                self.animations['fighting_right'].set_animation_phase(self.animations['facing_right'].get_animation_phase())

            self.screen_x = self.target_x
            self.screen_y = self.target_y

        if keys_pressed['space'] and (time.time() - self.last_move_time >= self.move_delay):
            self.fight()

        dx = keys_pressed['right'] - keys_pressed['left']
        dy = keys_pressed['up'] - keys_pressed['down']
        if (dx != 0 or dy != 0) and (time.time() - self.last_move_time >= self.move_delay):
            self.move(dx, dy, walkable_tiles)

        # if self.screen_x != self.target_x or self.screen_y != self.target_y:
        #     factor = min(1, (time.time() - self.last_move_time) / self.move_delay)
        #     self.screen_x += (self.target_x - self.screen_x) * factor
        #     self.screen_y += (self.target_y - self.screen_y) * factor

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
        self.last_move_time = time.time()

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
        self.last_move_time = time.time()


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_update_rate(1/60)
        # Background texture
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.background_texture = arcade.load_texture("resources/background_image.webp")  # Load the background image

        # Player character and controls
        self.player_character = PlayerCharacter(5, GRID_ROWS // 2, CELL_SIZE, MOVEMENT_DELAY)
        self.keys_pressed = {'left': 0, 'right': 0, 'up': 0, 'down': 0, 'space': 0}

        self.stuff = [
            StationarySprite(
                position_x=20,
                position_y=2,
                cell_size=CELL_SIZE,
                image_file="resources/character_standing_still.png",
                bottom_padding=10,
                cell_size_factor=1.8,
                margin_x=-5
            )
        ]

        # Init some random trees
        self.trees = self.create_border_trees()
        for _ in range(7):
            self.trees.append(Tree1(*self.random_empty_coordinates()))
        for _ in range(5):
            self.trees.append(Tree2(*self.random_empty_coordinates()))
        self.trees = sorted(self.trees, key=lambda t: t.grid_y, reverse=True)


    def create_border_trees(self):
        border_trees = []
        left_coords = [(4, 0), (4, 1), (3, 2), (3, 3), (2, 4), (2, 5), (1, 6), (1, 7), (0, 8), (0, 9)]
        for x, y in left_coords:
            for loop_x in range(0, x + 1):
                border_trees.append(Tree1(loop_x, y))

        right_coords = [(25, 0), (25, 1), (26, 2), (26, 3), (27, 4), (27, 5), (28, 6), (28, 7), (29, 8), (29, 9)]
        for x, y in right_coords:
            for loop_x in range(x, GRID_COLUMNS):
                border_trees.append(Tree1(loop_x, y))
        return border_trees

    def random_empty_coordinates(self):
        empty_spots = self.walkable_tiles
        x, y = random.randint(0, GRID_COLUMNS - 1), random.randint(0, GRID_ROWS - 1)
        while not empty_spots[y, x]:
            x, y = random.randint(0, GRID_COLUMNS - 1), random.randint(0, GRID_ROWS - 1)
        return x, y

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()

        # Draw the background image, scaled to fit the screen
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background_texture)

        # Draw the grid with perspective
        draw_grid = True
        empty_tiles = self.walkable_tiles
        if draw_grid:
            for y in range(GRID_ROWS):
                perspective_factor = calculate_perspective_factor(y)
                cell_width = CELL_SIZE * perspective_factor
                cell_height = CELL_SIZE * perspective_factor
                for x in range(GRID_COLUMNS):
                    screen_x = x * cell_width + (SCREEN_WIDTH / 2) - (GRID_COLUMNS * cell_width / 2)
                    screen_y = y * cell_height + BOTTOM_GRID_PAD + HORIZONTAL_PADDING * y
                    alpha = 40
                    color = (0, 0, 0, alpha) if empty_tiles[y, x] else (225, 0, 0, alpha + 40)
                    arcade.draw_rectangle_outline(screen_x + cell_width / 2, screen_y + cell_height / 2,
                                                  cell_width, cell_height, color, 3)
                    # arcade.draw_line_strip(
                    #     [(screen_x, screen_y - cell_height), (screen_x + cell_width, screen_y - cell_height)], (255,255,255,127), 2
                    # )

        for drawable in sorted(self.drawables, key=lambda t: t.grid_y, reverse=True):
            drawable.draw()  # Draw the tree or player

    @property
    def drawables(self):
        return [self.player_character] + self.trees + self.stuff

    @property
    def walkable_tiles(self) -> np.ndarray:
        grid = np.ones((GRID_ROWS, GRID_COLUMNS), bool)
        for d in self.drawables:
            grid[d.grid_y, d.grid_x] = False
        return grid

    def on_update(self, delta_time):
        """ Update game logic based on key states. """
        self.player_character.update(delta_time, self.keys_pressed, self.walkable_tiles)

    def on_key_press(self, key, modifiers):
        """ Handle key presses for player movement. """
        if key in {arcade.key.A, arcade.key.LEFT}:
            self.keys_pressed['left'] = 1
        elif key in {arcade.key.D, arcade.key.RIGHT}:
            self.keys_pressed['right'] = 1
        elif key in {arcade.key.W, arcade.key.UP}:
            self.keys_pressed['up'] = 1
        elif key in {arcade.key.S, arcade.key.DOWN}:
            self.keys_pressed['down'] = 1
        elif key in {arcade.key.SPACE}:
            self.keys_pressed['space'] = 1

    def on_key_release(self, key, modifiers):
        """ Handle key releases. """
        if key in {arcade.key.A, arcade.key.LEFT}:
            self.keys_pressed['left'] = 0
        elif key in {arcade.key.D, arcade.key.RIGHT}:
            self.keys_pressed['right'] = 0
        elif key in {arcade.key.W, arcade.key.UP}:
            self.keys_pressed['up'] = 0
        elif key in {arcade.key.S, arcade.key.DOWN}:
            self.keys_pressed['down'] = 0
        elif key in {arcade.key.SPACE}:
            self.keys_pressed['space'] = 0


def main():
    """ Main method """
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()

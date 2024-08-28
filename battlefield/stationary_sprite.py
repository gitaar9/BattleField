import random
from copy import deepcopy
import arcade
from PIL import ImageEnhance

from draw_utils import calculate_perspective_factor
from game_constants import BOTTOM_GRID_PAD, HORIZONTAL_PADDING, SCREEN_WIDTH, GRID_COLUMNS


class StationarySprite:
    def __init__(self, position_x, position_y, cell_size, image_file, bottom_padding=1, cell_size_factor=1.3, random_placement_pixels=2, margin_x=0, random_horizontal_flip=False):
        self.grid_x = position_x
        self.grid_y = position_y
        self.cell_size = cell_size
        self.image_file = image_file
        self.margin_x = margin_x

        self.texture = arcade.load_texture(
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

from pathlib import Path
from typing import Optional, List, Union, Tuple

import PIL
import arcade
import argparse

from arcade import Texture
from arcade.resources import resolve_resource_path

# Parse arguments
parser = argparse.ArgumentParser(description="Load an image and set regions for animation parts.")
parser.add_argument("image_path", type=str, help="Path to the image containing all parts of the character.")
args = parser.parse_args()

# Constants for the window
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Simple Animator"


class PartTexture:
    def __init__(self, part_name, x0, y0, x1, y1, scale, texture: Texture):
        self.part_name = part_name
        # self.center_x = x0 * scale + 8 * scale
        # self.center_y = (SCREEN_HEIGHT - y0 * scale) - 8 * scale
        self.x0 = 8 * scale
        self.y0 = 8 * scale
        self.texture = texture
        self.half_width = self.texture.width / 2
        self.half_height = self.texture.height / 2


    def draw(self):
        self.texture.draw_sized(self.x0 + self.half_width, self.y0 + self.half_height, self.texture.width, self.texture.height, 0, 255)

    def hit_test(self, x, y):
        # Calculate the half-width and half-height

        # Check if the point (x, y) is within the bounds defined by center_x, center_y, width, and height
        if (self.x0 <= x < self.x0 + self.texture.width) and (self.y0 <= y < self.y0 + self.texture.height):
            in_image_x = x - self.x0
            in_image_y = y - self.y0
            color = self.texture.image.getpixel((in_image_x, in_image_y))
            print(self.part_name, color)
            if color[3] > 0:
                return True
        return False




def load_parts(file_name: Union[str, Path],
               part_descriptions: List[Tuple],
               scale=1,
               hit_box_algorithm: Optional[str] = "Simple",
               hit_box_detail: float = 4.5) -> List[PartTexture]:
    """
    :param str file_name: Name of the file to that holds the texture.
    :param List part_descriptions:
    :param int scale:
    :param str hit_box_algorithm: One of None, 'None', 'Simple' (default) or 'Detailed'.
    :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box
    :returns List: List of :class:`Texture` objects.
    """

    texture_list = []

    # If we should pull from local resources, replace with proper path
    file_name = resolve_resource_path(file_name)

    source_image = PIL.Image.open(file_name).convert('RGBA')
    for part_name, (x0, y0), (x1, y1) in part_descriptions:
        image = source_image.crop((x0, y0, x1 + 1, y1 + 1))
        upscaled_image = image.resize((image.width * scale, image.height * scale), PIL.Image.NEAREST)

        texture = Texture(
            f"{file_name}-{part_name}",
            image=upscaled_image,
            hit_box_algorithm=hit_box_algorithm,
            hit_box_detail=hit_box_detail,
        )
        texture_list.append(PartTexture(part_name, x0, y0, x1, y1, scale, texture))

    return texture_list


class MyGame(arcade.Window):
    def __init__(self, width, height, title, image_path):
        super().__init__(width, height, title)
        arcade.set_background_color((200, 200, 200))
        self.image_path = image_path
        self.scale = 8
        self.parts = load_parts(
            file_name=self.image_path,
            part_descriptions=[
                ("Upper right arm", (26, 26), (33, 34)),
                ("Lower right arm", (26, 35), (33, 42)),
                ("Right hand", (28, 43), (33, 47)),

                ("Head", (18, 5), (34, 18)),

                ("Torso", (1, 3), (15, 21)),

                ("Upper right leg", (0, 29), (8, 35)),
                ("Lower right leg", (0, 36), (7, 46)),

                ("Upper left leg", (9, 28), (16, 35)),
                ("Lower left leg", (9, 36), (17, 46)),

                ("Upper left arm", (18, 26), (25, 34)),
                ("Lower left arm", (18, 35), (25, 42)),
                ("Left hand", (20, 43), (25, 47)),
            ],
            scale=self.scale
        )
        self.selected_part = None
        self.offset_x = 0
        self.offset_y = 0

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        for part in reversed(self.parts):
            part.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for part in self.parts:
                if part.hit_test(x, y):
                    self.selected_part = part
                    self.offset_x = part.x0 - x
                    self.offset_y = part.y0 - y
                    break

    def on_mouse_release(self, x, y, button, modifiers):
        self.selected_part = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.selected_part and buttons & arcade.MOUSE_BUTTON_LEFT:
            # Calculate new coordinates with the offset
            new_x = x + self.offset_x
            new_y = y + self.offset_y

            # Snap new_x and new_y to the nearest multiple of 8
            snapped_x = round(new_x / self.scale) * self.scale
            snapped_y = round(new_y / self.scale) * self.scale

            # Update the part's center coordinates
            self.selected_part.x0 = snapped_x
            self.selected_part.y0 = snapped_y


if __name__ == "__main__":
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, args.image_path)
    arcade.run()
